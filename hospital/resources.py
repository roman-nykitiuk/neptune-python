from import_export import resources, fields, widgets
from django.core.exceptions import ObjectDoesNotExist

from account.models import User
from device.models import Product
from hospital.models import Account, Client, Role, Item, Device
from price.constants import COST_TYPES, PRE_DOCTOR_ORDER, UNIT_COST, VALUE_DISCOUNT, PERCENT_DISCOUNT
from price.models import Discount, ClientPrice


class AccountResource(resources.ModelResource):
    name = fields.Field(attribute='user__name', column_name='name')
    email = fields.Field(attribute='user__email', column_name='email')
    role = fields.Field(attribute='role__name', column_name='role')
    client = fields.Field(attribute='client__name', column_name='client')

    class Meta:
        model = Account
        fields = ('id', 'name', 'email', 'role', 'client')
        export_order = ('id', 'name', 'email', 'role', 'client')

    def init_instance(self, row=None):
        instance = super().init_instance(row)
        try:
            user = User.objects.get(email=row.get('email'))
        except ObjectDoesNotExist:
            user = User(email=row.get('email'), name=row.get('name'))
            user.save()
        instance.user = user
        instance.client = Client.objects.get(name=row.get('client'))
        instance.role = Role.objects.get(name=row.get('role'))
        return instance

    def after_save_instance(self, instance, using_transactions, dry_run):
        instance.user.save()


class ItemResource(resources.ModelResource):
    client_name = fields.Field(attribute='device__client__name', column_name='Hospital name')
    manufacturer_name = fields.Field(attribute='device__product__manufacturer__name', column_name='Manufacturer name')
    hospital_number = fields.Field(attribute='device__hospital_number', column_name='Hospital part #',
                                   widget=widgets.CharWidget())
    model_number = fields.Field(attribute='device__product__model_number', column_name='Manufacturer part #',
                                widget=widgets.CharWidget())
    cost_type = fields.Field(attribute='cost_type', column_name='Cost type')
    serial_number = fields.Field(attribute='serial_number', column_name='Serial number', widget=widgets.CharWidget())
    lot_number = fields.Field(attribute='lot_number', column_name='Lot number', widget=widgets.CharWidget())
    purchased_date = fields.Field(attribute='purchased_date', column_name='Purchased date', widget=widgets.DateWidget())
    expired_date = fields.Field(attribute='expired_date', column_name='Expiry date', widget=widgets.DateWidget())
    bulk_discount_percent = fields.Field(attribute='bulk_discount_percent', column_name='Bulk discount percent',
                                         widget=widgets.NumberWidget())
    bulk_discount_value = fields.Field(attribute='bulk_discount_value', column_name='Bulk discount value',
                                       widget=widgets.NumberWidget())
    discount_order = fields.Field(attribute='discount_order', column_name='Discount order',
                                  widget=widgets.NumberWidget())
    discount_start_date = fields.Field(attribute='discount_start_date', column_name='Discount start date',
                                       widget=widgets.DateWidget())
    discount_end_date = fields.Field(attribute='discount_end_date', column_name='Discount end date',
                                     widget=widgets.DateWidget())

    COST_TYPES_DICT = dict((name, value) for value, name in COST_TYPES)

    class Meta:
        model = Item
        fields = ('id', 'client_name', 'manufacturer_name', 'hospital_number', 'model_number',
                  'serial_number', 'lot_number', 'purchased_date', 'expired_date', 'cost_type',
                  'bulk_discount_percent', 'bulk_discount_value', 'discount_order',
                  'discount_start_date', 'discount_end_date')
        export_order = ('id', 'client_name', 'manufacturer_name', 'hospital_number', 'model_number',
                        'serial_number', 'lot_number', 'purchased_date', 'expired_date', 'cost_type',
                        'bulk_discount_percent', 'bulk_discount_value', 'discount_order',
                        'discount_start_date', 'discount_end_date')

    @staticmethod
    def _build_bulk_discount(item):
        return (item.id and item.bulk_discount) or Discount()

    def dehydrate_cost_type(self, item):
        return item.get_cost_type_display()

    def dehydrate_bulk_discount_percent(self, item):
        return self._build_bulk_discount(item).percent

    def dehydrate_bulk_discount_value(self, item):
        return self._build_bulk_discount(item).value

    def dehydrate_discount_order(self, item):
        return self._build_bulk_discount(item).order

    def dehydrate_discount_start_date(self, item):
        return self._build_bulk_discount(item).start_date

    def dehydrate_discount_end_date(self, item):
        return self._build_bulk_discount(item).end_date

    def get_field_value(self, field_name, row, default=None):
        return row.get(self.fields.get(field_name).column_name) or default

    def before_import_row(self, row, **kwargs):
        field = 'cost_type'
        row[self.fields[field].column_name] = self.COST_TYPES_DICT.get(self.get_field_value(field, row), UNIT_COST)

    def init_instance(self, row=None):
        instance = super().init_instance(row)
        client = Client.objects.get(name=self.get_field_value('client_name', row))
        product = Product.objects.get(model_number=self.get_field_value('model_number', row))
        instance.device = Device.objects.get_or_create(client=client, product=product)[0]
        return instance

    def get_or_init_instance(self, instance_loader, row):
        instance, created = super().get_or_init_instance(instance_loader, row)

        hospital_number = self.get_field_value('hospital_number', row)
        if hospital_number and (instance.device.hospital_number != hospital_number):
            device = instance.device
            device.hospital_number = hospital_number
            device.save()

        bulk_discount_percent = self.get_field_value('bulk_discount_percent', row, default=0)
        bulk_discount_value = self.get_field_value('bulk_discount_value', row, default=0)
        if bulk_discount_percent or bulk_discount_value:
            device = instance.device
            client_price = ClientPrice.objects.get_or_create(client=device.client, product=device.product)[0]
            bulk_discount = client_price.discount_set.get_or_create(
                name='Bulk',
                cost_type=self.get_field_value('cost_type', row),
                order=self.get_field_value('discount_order', row),
                start_date=self.get_field_value('discount_start_date', row, default=None),
                end_date=self.get_field_value('discount_end_date', row, default=None),
                apply_type=PRE_DOCTOR_ORDER,
                discount_type=PERCENT_DISCOUNT if bulk_discount_percent > 0 else VALUE_DISCOUNT,
                percent=bulk_discount_percent,
                value=bulk_discount_value,
            )[0]
            instance.build_bulk_discount(bulk_discount)

        return instance, created

    def after_save_instance(self, instance, using_transactions, dry_run):
        another_cost_type_orphan_discounts = instance.discounts.exclude(cost_type=instance.cost_type).all()
        instance.discounts.remove(*another_cost_type_orphan_discounts)
        instance.save_bulk_discount()
