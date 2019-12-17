from decimal import Decimal

from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.db.models import Sum, Q
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from django_fsm import transition, FSMIntegerField

from neptune.models import SharedImage
from price.constants import UNIT_COST, SYSTEM_COST, PERCENT_DISCOUNT, COST_TYPES, DISCOUNT_TYPES, \
    DISCOUNT_APPLY_TYPES, ON_DOCTOR_ORDER, SPEND, MARKETSHARE, TIER_TYPES, POST_DOCTOR_ORDER, PURCHASED_UNITS, \
    NEW_REBATE, COMPLETE_REBATE, REBATE_STATUSES, REBATABLE_ITEM_TYPES, ELIGIBLE_ITEM, REBATED_ITEM, USED_UNITS, \
    PRE_DOCTOR_ORDER
from price.managers import DiscountQuerySet


class ClientPrice(models.Model):
    product = models.ForeignKey('device.Product', on_delete=models.CASCADE)
    client = models.ForeignKey('hospital.Client', on_delete=models.CASCADE, null=True, blank=False)
    unit_cost = models.DecimalField(_('Unit cost'), max_digits=20, decimal_places=2, default=0)
    system_cost = models.DecimalField(_('System cost'), max_digits=20, decimal_places=2, default=0)

    class Meta:
        unique_together = ('product', 'client')

    def __str__(self):
        return (f'{self.client.name}: '
                f'Unit Price=${self.unit_cost} - System Price=${self.system_cost}')

    def original_cost(self, cost_type):
        if cost_type == UNIT_COST:
            return self.unit_cost
        else:
            return self.system_cost

    def discounts(self, cost_type):
        return self.discount_set.filter(cost_type=cost_type).order_by('apply_type', 'order').all()

    @property
    def unit_cost_discounts(self):
        return self.discounts(UNIT_COST)

    @property
    def system_cost_discounts(self):
        return self.discounts(SYSTEM_COST)

    def redeem(self, discounts, item):
        original_cost = cost = self.original_cost(item.cost_type)
        if not isinstance(discounts, QuerySet):
            discount_ids = [discount.id for discount in discounts]
            discounts = Discount.objects.filter(id__in=discount_ids)
        discounts = discounts.filter(cost_type=item.cost_type).order_by('order')

        previous_order = None
        previous_order_discounts_value = 0
        total_discounted_value = 0
        point_of_sales_saving = 0
        redeemed_discounts = []
        for discount in discounts:
            if previous_order and previous_order < discount.order:
                cost -= previous_order_discounts_value
                previous_order_discounts_value = 0

            value = discount.get_value(cost)
            if discount.apply_type in [PRE_DOCTOR_ORDER, POST_DOCTOR_ORDER]:
                purchased_date = item.purchased_date
            elif item.rep_case:
                purchased_date = item.rep_case.procedure_date
            else:
                purchased_date = None

            valid_discount = discount.is_valid(purchased_date)
            redeemed_discounts.append({
                'discount': discount,
                'is_valid': valid_discount,
                'value': value,
            })
            value = (valid_discount * value) or 0

            total_discounted_value += value
            if discount.apply_type == ON_DOCTOR_ORDER:
                point_of_sales_saving += value

            previous_order_discounts_value += value
            previous_order = discount.order

        return {
            'original_cost': original_cost,
            'total_cost': original_cost - total_discounted_value,
            'point_of_sales_saving': point_of_sales_saving,
            'redeemed_discounts': redeemed_discounts,
        }

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.client.device_set.get_or_create(product=self.product)


class DiscountBase(models.Model):
    order = models.PositiveSmallIntegerField(default=1)
    percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, null=True, blank=True)
    value = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True, blank=True)
    discount_type = models.PositiveSmallIntegerField(_('Discount type'), choices=DISCOUNT_TYPES,
                                                     default=PERCENT_DISCOUNT)

    class Meta:
        abstract = True


class Discount(DiscountBase):
    name = models.CharField(_('Discount name'), max_length=255)
    cost_type = models.PositiveSmallIntegerField(_('Type'), choices=COST_TYPES)
    client_price = models.ForeignKey(ClientPrice, on_delete=models.CASCADE)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    apply_type = models.PositiveSmallIntegerField(_('Apply type'), choices=DISCOUNT_APPLY_TYPES,
                                                  default=ON_DOCTOR_ORDER)
    shared_image = models.ForeignKey(SharedImage, on_delete=models.CASCADE, null=True, blank=True)
    rebate = models.ForeignKey('price.Rebate', on_delete=models.SET_NULL, null=True, blank=True)

    objects = DiscountQuerySet.as_manager()

    def __str__(self):
        return self.name

    def is_valid(self, purchased_date=None):
        if purchased_date is None:
            return False

        if self.start_date and self.start_date > purchased_date:
            return False

        if self.end_date and self.end_date < purchased_date:
            return False

        return True

    def get_value(self, cost):
        if self.discount_type == PERCENT_DISCOUNT:
            return Decimal(cost * (self.percent or 0) / Decimal(100))
        else:
            return self.value

    @property
    def display_name(self):
        if self.discount_type == PERCENT_DISCOUNT:
            discount = f'-{self.percent}%'
        else:
            discount = f'-${self.value}'

        return f'{self.name} {discount}'


class RebatableItem(models.Model):
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        limit_choices_to=Q(app_label='device') & (Q(model='specialty') | Q(model='category') | Q(model='product'))
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    item_type = models.PositiveSmallIntegerField(choices=REBATABLE_ITEM_TYPES, default=ELIGIBLE_ITEM)
    rebate = models.ForeignKey('Rebate', on_delete=models.CASCADE, related_name='rebatable_items')

    class Meta:
        unique_together = ('content_type', 'object_id', 'rebate', 'item_type')

    def __str__(self):
        return f'{self.content_type.model}: {self.content_object}'

    @property
    def product_ids(self):
        content_object = self.content_object
        if self.content_type.model == 'product':
            return [content_object.id]
        elif self.content_type.model == 'category':
            return list(content_object.product_set.distinct().values_list('id', flat=True))
        elif self.content_type.model == 'specialty':
            return list(content_object.category_set.distinct().values_list('product__id', flat=True))
        return []


class Rebate(models.Model):
    name = models.CharField(_('Rebate program'), max_length=255)
    client = models.ForeignKey('hospital.Client', on_delete=models.CASCADE)
    manufacturer = models.ForeignKey('device.Manufacturer', on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = FSMIntegerField(default=NEW_REBATE, choices=REBATE_STATUSES)

    def __str__(self):
        return f'{self.name}: {self.start_date} - {self.end_date}'

    @property
    def eligible_items(self):
        return self.rebatable_items.filter(item_type=ELIGIBLE_ITEM)

    @property
    def rebated_items(self):
        return self.rebatable_items.filter(item_type=REBATED_ITEM)

    def rebatable_product_ids(self, rebatable_items):
        product_ids = []
        for rebatable_item in rebatable_items.all():
            product_ids += rebatable_item.product_ids
        return product_ids

    def get_device_items(self, rebatable_items):
        Item = apps.get_model(app_label='hospital', model_name='item')
        filter_attrs = dict(
            device__client=self.client,
            device__product__manufacturer=self.manufacturer,
        )

        if rebatable_items.exists():
            filter_attrs['device__product__id__in'] = self.rebatable_product_ids(rebatable_items)
        if self.start_date:
            filter_attrs['purchased_date__gte'] = self.start_date
        if self.end_date:
            filter_attrs['purchased_date__lte'] = self.end_date

        return Item.objects.filter(**filter_attrs)

    @transition(field=status, source=NEW_REBATE, target=COMPLETE_REBATE)
    @transaction.atomic
    def apply(self):
        eligible_purchased_items = self.get_device_items(self.eligible_items)
        rebated_purchased_items = self.get_device_items(self.rebated_items)

        for tier in self.tier_set.all():
            if tier.is_valid(eligible_purchased_items):
                rebate_discount_attrs = dict(
                    name=f'{self.name}: {tier}',
                    apply_type=POST_DOCTOR_ORDER,
                    order=tier.order,
                    discount_type=tier.discount_type,
                    start_date=tier.rebate.start_date,
                    end_date=tier.rebate.end_date,
                    rebate=self
                )
                if tier.discount_type == PERCENT_DISCOUNT:
                    rebate_discount_attrs['percent'] = tier.percent
                else:
                    rebate_discount_attrs['value'] = tier.value

                for item in rebated_purchased_items:
                    client_price = self.client.clientprice_set.get(product=item.device.product)
                    rebate_discount = Discount.objects.get_or_create(
                        cost_type=item.cost_type,
                        client_price=client_price,
                        **rebate_discount_attrs
                    )[0]
                    item.discounts.add(rebate_discount)

        for item in rebated_purchased_items:
            item.refresh_cost()
            item.save(update_app=item.is_used)

    @transition(field=status, source=COMPLETE_REBATE, target=NEW_REBATE)
    @transaction.atomic
    def unapply(self):
        applied_rebate_discounts = self.discount_set.all()
        for discount in applied_rebate_discounts:
            discount.delete()

        rebated_purchased_items = self.get_device_items(self.rebated_items)
        for item in rebated_purchased_items:
            item.refresh_cost()
            item.save(update_app=item.is_used)


class Tier(DiscountBase):
    tier_type = models.PositiveSmallIntegerField(_('Tier type'), choices=TIER_TYPES, default=SPEND)
    lower_bound = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    upper_bound = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    rebate = models.ForeignKey(Rebate, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.get_tier_type_display()} in range ({self.lower_bound}, {self.upper_bound})'

    def marketshare(self, eligible_purchased_items):
        client_total_spend = self.rebate.client.items.filter(
            purchased_date__gte=self.rebate.start_date,
            purchased_date__lte=self.rebate.end_date
        ).aggregate(spend=Sum('cost'))['spend']

        if client_total_spend:
            spend = self.spend(eligible_purchased_items)
            return float((spend / client_total_spend) * 100)
        else:
            return 0

    def spend(self, eligible_purchased_items):
        return eligible_purchased_items.aggregate(spend=Sum('cost'))['spend'] or 0

    def purchased_units(self, eligible_purchased_items):
        return eligible_purchased_items.count()

    def used_units(self, eligible_purchased_items):
        return eligible_purchased_items.filter(is_used=True).count()

    def is_valid(self, eligible_purchased_items):
        if self.tier_type == SPEND:
            value = self.spend(eligible_purchased_items)
        elif self.tier_type == MARKETSHARE:
            value = self.marketshare(eligible_purchased_items)
        elif self.tier_type == PURCHASED_UNITS:
            value = self.purchased_units(eligible_purchased_items)
        elif self.tier_type == USED_UNITS:
            value = self.used_units(eligible_purchased_items)

        return (value >= self.lower_bound) and (value <= self.upper_bound if self.upper_bound else True)
