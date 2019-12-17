import os

from django.test import TestCase
from tablib import Dataset

from account.factories import UserFactory
from account.models import User
from device.factories import ManufacturerFactory, ProductFactory
from hospital.constants import RolePriority
from hospital.factories import ClientFactory, RoleFactory, ItemFactory
from hospital.models import Account, Item
from hospital.resources import AccountResource, ItemResource
from neptune.settings.base import FIXTURE_DIR
from price.constants import SYSTEM_COST, UNIT_COST, PRE_DOCTOR_ORDER, ON_DOCTOR_ORDER, PERCENT_DISCOUNT
from price.factories import ClientPriceFactory, DiscountFactory
from price.models import Discount


class AccountResourceTestCase(TestCase):
    def setUp(self):
        self.client = ClientFactory(name='PETCARE')
        self.physician_role = RoleFactory(name='Physician', priority=RolePriority.PHYSICIAN.value)
        self.admin_role = RoleFactory(name='Hospital Admin', priority=RolePriority.ADMIN.value)
        self.user = UserFactory(email='benny@petcare.com', name='Old Benny Name')

    def test_import_from_xls_file(self):
        account_resource = AccountResource()
        dataset = Dataset().load(open(os.path.join(FIXTURE_DIR, 'account.xls'), 'rb').read())

        self.assertEqual(User.objects.count(), 1)
        account_resource.import_data(dataset)

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Account.objects.count(), 2)
        account_1, account_2 = Account.objects.all()
        self.assertEqual(account_1.role, self.physician_role)
        self.assertEqual(account_1.client, self.client)
        self.assertEqual(account_2.role, self.admin_role)
        self.assertEqual(account_2.client, self.client)

        updated_user = User.objects.get(email='benny@petcare.com')
        self.assertEqual(updated_user.name, 'Benny The Bear')
        new_user = User.objects.get(email='kitty@petcare.com')
        self.assertEqual(new_user.name, 'Kitty Galore')


class ItemResourceTestCase(TestCase):
    def setUp(self):
        self.client = ClientFactory(name='UVMC')
        manufacturer = ManufacturerFactory(name='Medtronic')
        self.product = ProductFactory(model_number='SESR01', manufacturer=manufacturer)
        client_price = ClientPriceFactory(product=self.product, client=self.client)
        self.bulk_discount = DiscountFactory(name='Bulk', client_price=client_price, apply_type=PRE_DOCTOR_ORDER,
                                             cost_type=UNIT_COST, discount_type=PERCENT_DISCOUNT, percent=10, value=0,
                                             order=1)
        self.discount_2 = DiscountFactory(client_price=client_price, apply_type=ON_DOCTOR_ORDER, cost_type=SYSTEM_COST)
        self.device = self.product.device_set.get(client=self.client)
        self.device.hospital_number = '70669'
        self.device.save()
        self.item = ItemFactory(device=self.device, serial_number='PJN7204267', cost_type=SYSTEM_COST,
                                discounts=[self.discount_2])
        self.xls_file_path = os.path.join(FIXTURE_DIR, 'items.xls')
        self._prepare_xls_file()

    def _prepare_xls_file(self):
        headers = ('id', 'Hospital name', 'Manufacturer name', 'Hospital part #', 'Manufacturer part #',
                   'Serial number', 'Lot number', 'Purchased date', 'Expiry date', 'Cost type', 'Bulk discount percent',
                   'Bulk discount value', 'Discount order', 'Discount start date', 'Discount end date')
        data = [
            ('', 'UVMC', 'Medtronic', '', 'SESR01', 'PJN7204200', '', '2019-03-22', '', 'Unit cost',
             15, 0, 1, '', ''),
            (self.item.id, 'UVMC', 'Medtronic', '80000', 'SESR01', 'PJN7204267', '', '2019-03-28', '', 'Unit cost',
             10, 0, 1, '', ''),
            ('', 'UVMC', 'Medtronic', '', 'SESR01', '', '31232123', '2019-03-22', '', 'System cost',
             0, 20, 1, '', ''),
        ]
        dataset = Dataset(*data, headers=headers)
        with open(self.xls_file_path, 'wb') as f:
            f.write(dataset.export('xls'))

    def test_import_from_xls_file(self):
        item_resource = ItemResource()
        dataset = Dataset().load(open(self.xls_file_path, 'rb').read())

        self.assertEqual(Item.objects.count(), 1)
        item_resource.import_data(dataset)
        self.assertEqual(Item.objects.count(), 3)
        self.assertEqual(Discount.objects.count(), 4)
        bulk_discount_2 = Discount.objects.get(name='Bulk', percent=15, cost_type=UNIT_COST)
        bulk_discount_3 = Discount.objects.get(name='Bulk', value=20, cost_type=SYSTEM_COST)
        self.assertCountEqual(Discount.objects.all(), [self.bulk_discount, self.discount_2,
                                                       bulk_discount_2, bulk_discount_3])

        item_1, item_2, item_3 = Item.objects.all().order_by('id')
        self.assertEqual(str(item_1.purchased_date), '2019-03-28')
        self.assertEqual(item_1.cost_type, UNIT_COST)
        self.assertEqual(item_1.device, self.device)
        self.device.refresh_from_db()
        self.assertEqual(self.device.hospital_number, '80000')
        self.assertCountEqual(item_1.discounts.all(), [self.bulk_discount])

        self.assertEqual(item_2.device, self.device)
        self.assertEqual(item_2.serial_number, 'PJN7204200')
        self.assertEqual(str(item_2.purchased_date), '2019-03-22')
        self.assertEqual(item_2.cost_type, UNIT_COST)
        self.assertCountEqual(item_2.discounts.all(), [bulk_discount_2])

        self.assertEqual(item_3.device, self.device)
        self.assertEqual(item_3.lot_number, '31232123')
        self.assertEqual(str(item_3.purchased_date), '2019-03-22')
        self.assertEqual(item_3.cost_type, SYSTEM_COST)
        self.assertCountEqual(item_3.discounts.all(), [bulk_discount_3])
