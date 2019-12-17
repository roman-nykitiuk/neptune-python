from functools import partial

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from hospital.constants import COUNTRIES
from hospital.converter import int_to_b32
from hospital.managers import ItemQuerySet
from neptune.utils import make_imagefield_filepath
from price.constants import COST_TYPES, UNIT_COST, NOT_IMPLANTED_REASONS, PRE_DOCTOR_ORDER
from tracker.models import PurchasePrice
from hospital.constants import RolePriority, PURCHASE_TYPES, BULK_PURCHASE, PRODUCT_ITEM_INDENTIFIER_SIZE

User = get_user_model()


class Client(models.Model):
    name = models.CharField(_('Client name'), max_length=255, null=False, blank=False)
    street = models.CharField(_('Street address'), max_length=255, null=False, blank=False)
    city = models.CharField(_('City'), max_length=255, null=False, blank=False)
    state = models.CharField(_('State'), max_length=255, null=False, blank=False)
    country = models.CharField(_('Country'), max_length=255, null=False, blank=False, choices=COUNTRIES, default='US')
    image = models.ImageField(upload_to=partial(make_imagefield_filepath, 'clients'), null=True, blank=True)
    contact_name = models.CharField(_('Contact name'), max_length=127, null=True, blank=True)
    contact_phone = models.CharField(_('Phone'), max_length=20, null=True, blank=True)
    contact_email = models.EmailField(_('Email'), null=True, blank=True)
    products = models.ManyToManyField('device.Product', through='hospital.Device')
    notes = models.TextField(_('Notes'), null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)
    users = models.ManyToManyField(User, through='hospital.Account')

    def __str__(self):
        return self.name

    def devices_by_specialties(self):
        devices_by_specialties = {}
        products = self.products.select_related('category__specialty').all()
        for product in products:
            specialty = product.category.specialty
            specialty_dict = devices_by_specialties.get(specialty.id, {'name': specialty.name})
            specialty_devices = specialty_dict.get('products', [])
            specialty_devices.append((product.id, product.name))
            specialty_dict['products'] = specialty_devices
            devices_by_specialties[specialty.id] = specialty_dict
        return devices_by_specialties

    def set_children(self, children_ids):
        children = Client.objects.filter(id__in=children_ids)
        self.children.set(children)

    @property
    def root_parent_id(self):
        if self.parent:
            return self.parent.root_parent_id
        else:
            return self.id

    @property
    def items(self):
        return Item.objects.filter(device__client=self).distinct()


class Role(models.Model):
    name = models.CharField(max_length=255, default='Physician', unique=True)
    priority = models.PositiveSmallIntegerField(default=RolePriority.default().value,
                                                choices=RolePriority.to_field_choices())

    class Meta:
        verbose_name = 'user role'
        unique_together = ('name', 'priority')

    def __str__(self):
        return self.name


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    specialties = models.ManyToManyField('device.Specialty')

    class Meta:
        verbose_name = 'user account'
        unique_together = ('user', 'client')

    def __str__(self):
        return f'{self.role.name} {self.user.email}'


class Item(models.Model):
    device = models.ForeignKey('hospital.Device', on_delete=models.CASCADE)
    rep_case = models.ForeignKey('tracker.RepCase', on_delete=models.SET_NULL, null=True, blank=True)
    serial_number = models.CharField(_('Serial number'), max_length=255, null=True, blank=True, unique=True)
    lot_number = models.CharField(_('Lot number'), max_length=255, null=True, blank=True)
    identifier = models.CharField(_('Identifier number'), max_length=255, unique=True)
    expired_date = models.DateField(_('Expiry date'), null=True, blank=True)
    purchased_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    saving = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    is_used = models.BooleanField(_('Is used'), default=False)
    purchase_type = models.SmallIntegerField(_('Purchased type'), choices=PURCHASE_TYPES, default=BULK_PURCHASE)
    discounts = models.ManyToManyField('price.Discount')
    cost_type = models.PositiveSmallIntegerField(_('Cost type'), choices=COST_TYPES, default=UNIT_COST)
    not_implanted_reason = models.PositiveSmallIntegerField(_('Not implanted reason'), choices=NOT_IMPLANTED_REASONS,
                                                            null=True, blank=True)

    __original_is_used = None

    objects = ItemQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'Serial numbers'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_is_used = self.is_used
        self.__bulk_discount = None

    def __str__(self):
        return f'{self.device.hospital_number}: {self.identifier} expired on {self.expired_date}'

    def update_item_identifier(self):
        if self.id:
            persistent_item = Item.objects.get(pk=self.id)
            if persistent_item.lot_number != self.lot_number or persistent_item.serial_number != self.serial_number:
                self.update_identifier()
        else:
            self.update_identifier()

    def update_identifier(self):
        if (self.serial_number is not None) and self.serial_number.strip() == '':
            self.serial_number = None

        if not (self.serial_number or self.lot_number):
            raise AttributeError('Either serial number or lot number must be present.')

        max_pk_item = self.__class__.objects.order_by('-id').first()
        pk = self.pk if self.pk else (max_pk_item.pk + 1 if max_pk_item else 1)
        self.identifier = self.serial_number or f'{self.lot_number}-{int_to_b32(pk, PRODUCT_ITEM_INDENTIFIER_SIZE)}'

    def update_app(self):
        if self.rep_case and self.rep_case.procedure_date:
            year = self.rep_case.procedure_date.year
            PurchasePrice.update(
                category=self.device.product.category,
                client=self.device.client,
                year=year,
                level=self.device.product.level,
                cost_type=self.cost_type,
            )

    def save(self, *args, discounts=None, update_app=None, **kwargs):
        self.update_item_identifier()
        super().save(*args, **kwargs)

        if update_app is None:
            update_app = (self.__original_is_used != self.is_used) or (not self.id and self.is_used)
        if update_app:
            self.update_app()

    def save_bulk_discount(self):
        if self.__bulk_discount:
            self.discounts.add(self.__bulk_discount)
            self.__bulk_discount = None

    def build_bulk_discount(self, bulk_discount):
        self.__bulk_discount = bulk_discount

    def update_cost(self, discounts):
        try:
            client_price = self.device.product.clientprice_set.get(client=self.device.client)
            redemption = client_price.redeem(discounts, self)
            self.cost = redemption['total_cost']
            self.saving = redemption['point_of_sales_saving']
        except ObjectDoesNotExist:
            pass

    def refresh_cost(self):
        self.update_cost(self.discounts.all())

    @property
    def bulk_discount(self):
        bulk_discounts = self.discounts.filter(apply_type=PRE_DOCTOR_ORDER, cost_type=self.cost_type)
        return bulk_discounts.first()

    @property
    def discounts_as_table(self):
        return render_to_string('hospital/item/discounts.html', {
            'discounts': self.discounts.order_by('cost_type', 'order').all()
        })


class Device(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    product = models.ForeignKey('device.Product', on_delete=models.CASCADE)
    hospital_number = models.CharField(_('Hospital part number'), max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('client', 'product',)

    def __str__(self):
        return self.product.name
