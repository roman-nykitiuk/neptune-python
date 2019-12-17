from datetime import date
from random import randint
from shutil import rmtree

from django.conf import settings
from django.test import TestCase, override_settings
from factory.django import ImageField

from device.factories import ProductFactory, ManufacturerFactory
from hospital.constants import RolePriority
from hospital.factories import ItemFactory, AccountFactory, RoleFactory, DeviceFactory, ClientFactory
from hospital.models import Item
from price.constants import PRE_DOCTOR_ORDER, VALUE_DISCOUNT, ON_DOCTOR_ORDER, UNIT_COST
from price.factories import DiscountFactory, ClientPriceFactory
from tracker.factories import RepCaseFactory


@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class ItemQuerySetTestCase(TestCase):
    def tearDown(self):
        super().tearDown()
        rmtree(settings.MEDIA_ROOT)

    def setUp(self):
        self.client_1, self.client_2 = ClientFactory.create_batch(2)
        manufacturer = ManufacturerFactory(image=ImageField(filename='biotronik.jpg'))
        product = ProductFactory(manufacturer=manufacturer)
        self.item_1 = ItemFactory(cost=randint(110, 150), cost_type=UNIT_COST,
                                  device=DeviceFactory(client=self.client_1, product=product))
        self.item_2 = ItemFactory(cost=randint(210, 290), cost_type=UNIT_COST,
                                  device=DeviceFactory(client=self.client_1))
        self.item_3 = ItemFactory(cost=randint(400, 500), device=DeviceFactory(client=self.client_2))
        self.item_4 = ItemFactory(
            cost=1000, cost_type=UNIT_COST,
            device=DeviceFactory(client=self.client_1,
                                 product=ProductFactory(manufacturer=manufacturer, category=product.category))
        )
        physician_role = RoleFactory(priority=RolePriority.PHYSICIAN.value)
        self.physician_1 = AccountFactory(client=self.client_1, role=physician_role)
        self.physician_2 = AccountFactory(client=self.client_2, role=physician_role, user=self.physician_1.user)
        self.physician_3 = AccountFactory(client=self.client_1, role=physician_role)

    def test_used_by_client_queryset(self):
        self.assertCountEqual(self.client_1.items.used_by_client(self.client_1), [])
        self.assertCountEqual(self.client_1.items.used_by_client(self.client_2), [])

        RepCaseFactory(client=self.client_1, items=[self.item_1])
        RepCaseFactory(client=self.client_1, items=[self.item_2])
        RepCaseFactory(client=self.client_2, items=[self.item_3])
        self.assertCountEqual(self.client_1.items.used_by_client(self.client_1), [self.item_1, self.item_2])
        self.assertCountEqual(self.client_2.items.used_by_client(self.client_2), [self.item_3])

    def test_used_by_physician_queryset(self):
        physician_3 = AccountFactory(client=self.client_2, role=self.physician_2.role)
        self.assertEqual(Item.objects.used_by_physician(self.physician_1).count(), 0)
        self.assertEqual(Item.objects.used_by_physician(self.physician_2).count(), 0)
        self.assertEqual(Item.objects.used_by_physician(physician_3).count(), 0)

        RepCaseFactory(items=[self.item_1], physician=self.physician_1, client=self.client_1)
        RepCaseFactory(items=[self.item_2], physician=self.physician_1, client=self.client_1)
        RepCaseFactory(items=[self.item_3, self.item_4], physician=self.physician_2, client=self.client_2)
        RepCaseFactory(items=ItemFactory.create_batch(2), physician=physician_3, client=self.client_2)
        self.assertCountEqual(Item.objects.used_by_physician(self.physician_1), [self.item_1, self.item_2])
        self.assertCountEqual(Item.objects.used_by_physician(self.physician_2), [self.item_3, self.item_4])

    def test_used_in_period_queryset(self):
        RepCaseFactory(procedure_date=date(2018, 9, 10), items=[self.item_1, self.item_2])
        RepCaseFactory(procedure_date=date(2017, 10, 9), items=[self.item_3])
        RepCaseFactory(procedure_date=date(2018, 10, 9), items=[self.item_4])

        self.assertCountEqual(Item.objects.used_in_period(2017), [self.item_3])
        self.assertCountEqual(Item.objects.used_in_period(2017, month=9), [])
        self.assertCountEqual(Item.objects.used_in_period(2017, month=10), [self.item_3])

        self.assertCountEqual(Item.objects.used_in_period(2018), [self.item_1, self.item_2, self.item_4])
        self.assertCountEqual(Item.objects.used_in_period(2018, month=9), [self.item_1, self.item_2])
        self.assertCountEqual(Item.objects.used_in_period(2018, month=10), [self.item_4])

    def test_marketshare(self):
        self.assertCountEqual(self.client_1.items, [self.item_1, self.item_2, self.item_4])
        self.assertCountEqual(self.client_1.items.marketshare(), [{
            'manufacturer_short_name': self.item_1.device.product.manufacturer.short_name,
            'manufacturer_name': self.item_1.device.product.manufacturer.name,
            'manufacturer_image': 'manufacturers/biotronik.jpg',
            'manufacturer_id': self.item_1.device.product.manufacturer.id,
            'spend': float(self.item_1.cost + self.item_4.cost),
            'units': 2,
            'app': float((self.item_1.cost + self.item_4.cost) / 2),
        }, {
            'manufacturer_short_name': self.item_2.device.product.manufacturer.short_name,
            'manufacturer_name': self.item_2.device.product.manufacturer.name,
            'manufacturer_image': '',
            'manufacturer_id': self.item_2.device.product.manufacturer.id,
            'spend': float(self.item_2.cost),
            'units': 1,
            'app': float(self.item_2.cost),
        }])

        self.assertCountEqual(self.client_2.items, [self.item_3])
        self.assertCountEqual(self.client_2.items.marketshare(), [{
            'manufacturer_short_name': self.item_3.device.product.manufacturer.short_name,
            'manufacturer_name': self.item_3.device.product.manufacturer.name,
            'manufacturer_image': '',
            'manufacturer_id': self.item_3.device.product.manufacturer.id,
            'spend': float(self.item_3.cost),
            'units': 1,
            'app': float(self.item_3.cost),
        }])

    def test_physician_app(self):
        item_3 = ItemFactory(device=DeviceFactory(client=self.client_1), cost=randint(350, 370))
        item_5 = ItemFactory(device=DeviceFactory(client=self.client_1), cost=randint(100, 200))
        RepCaseFactory(client=self.client_1, physician=self.physician_1, items=[self.item_1, self.item_2])
        RepCaseFactory(client=self.client_1, physician=self.physician_3, items=[item_3])
        RepCaseFactory(client=self.client_1, physician=self.physician_3, items=[item_5])

        self.assertCountEqual(self.client_1.items, [self.item_1, self.item_2, item_3, self.item_4, item_5])
        self.assertCountEqual(self.client_1.items.physician_app(), [{
            'app': float((self.item_1.cost + self.item_2.cost) / 2),
            'physician_id': self.physician_1.id,
            'physician_name': self.physician_1.user.name,
        }, {
            'app': float((item_3.cost + item_5.cost) / 2),
            'physician_id': self.physician_3.id,
            'physician_name': self.physician_3.user.name,
        }, {
            'app': float(self.item_4.cost),
            'physician_id': None,
            'physician_name': None,
        }])

    def test_saving_by_categories_queryset(self):
        RepCaseFactory(client=self.client_1, physician=self.physician_1, items=[self.item_1, self.item_2])
        RepCaseFactory(client=self.client_1, physician=self.physician_3, items=[self.item_4])

        self.assertCountEqual(self.client_1.items.used_by_client(self.client_1).saving_by_categories(), [{
            'category_id': self.item_1.device.product.category.id,
            'category_name': self.item_1.device.product.category.name,
            'saving': 0,
            'spend': self.item_1.cost + self.item_4.cost,
        }, {
            'category_id': self.item_2.device.product.category.id,
            'category_name': self.item_2.device.product.category.name,
            'saving': 0,
            'spend': self.item_2.cost,
        }])

        bulk_discount = DiscountFactory(apply_type=PRE_DOCTOR_ORDER, discount_type=VALUE_DISCOUNT, value=10,
                                        cost_type=UNIT_COST)
        cco_discount = DiscountFactory(apply_type=ON_DOCTOR_ORDER, discount_type=VALUE_DISCOUNT, value=15,
                                       cost_type=UNIT_COST)
        repless_discount = DiscountFactory(apply_type=ON_DOCTOR_ORDER, discount_type=VALUE_DISCOUNT, value=20,
                                           cost_type=UNIT_COST)
        self.item_1.discounts.set([bulk_discount, cco_discount])
        self.item_2.discounts.set([bulk_discount, repless_discount])
        self.item_4.discounts.set([cco_discount, repless_discount])
        for item in [self.item_1, self.item_2, self.item_4]:
            ClientPriceFactory(client=self.client_1, product=item.device.product, unit_cost=item.cost)
            item.refresh_cost()
            item.save()

        self.assertCountEqual(self.client_1.items.used_by_client(self.client_1).saving_by_categories(), [{
            'category_id': self.item_1.device.product.category.id,
            'category_name': self.item_1.device.product.category.name,
            'saving': cco_discount.value * 2 + repless_discount.value,
            'spend': self.item_1.cost + self.item_4.cost,
        }, {
            'category_id': self.item_2.device.product.category.id,
            'category_name': self.item_2.device.product.category.name,
            'saving': repless_discount.value,
            'spend': self.item_2.cost,
        }])
