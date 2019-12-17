from calendar import month_name
from datetime import datetime, date
from decimal import Decimal
from shutil import rmtree

from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from factory.django import ImageField
from rest_framework import status

from api.tests.base import APIViewTestCase
from device.factories import CategoryFactory, ProductFactory, ManufacturerFactory
from device.constants import ProductLevel
from hospital.constants import RolePriority
from hospital.factories import ClientFactory, DeviceFactory, AccountFactory, ItemFactory, RoleFactory
from price.models import UNIT_COST, SYSTEM_COST
from tracker.factories import PurchasePriceFactory, RepCaseFactory


class PurchasePriceViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.client_1 = ClientFactory()
        AccountFactory(client=self.client_1, user=self.user, role=RoleFactory(priority=RolePriority.PHYSICIAN.value))
        self.category = CategoryFactory()
        self.path = reverse('api:hospital:tracker:app:purchase_price',
                            args=(self.client_1.id, self.category.id, 'entry', 'unit_cost'))
        PurchasePriceFactory(category=self.category, client=self.client_1, cost_type=UNIT_COST,
                             level=ProductLevel.ENTRY.value,
                             year=datetime.utcnow().year, min=1000, max=1200, avg=1100)
        PurchasePriceFactory(category=self.category, client=self.client_1, cost_type=SYSTEM_COST,
                             level=ProductLevel.ADVANCED.value,
                             year=datetime.utcnow().year, min=1200, max=1400, avg=1300)

    def test_api_path(self):
        self.assertEqual(self.path,
                         f'/api/clients/{self.client_1.id}/app/categories/{self.category.id}/entry/unit_cost')

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_get_method_return_purchased_unit_cost_aggregation(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {'min': '1000.00', 'max': '1200.00', 'avg': '1100.00'})

    def test_get_method_return_purchased_system_cost_aggregation(self):
        path = reverse('api:hospital:tracker:app:purchase_price',
                       args=(self.client_1.id, self.category.id, 'advanced', 'system_cost'))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {'min': '1200.00', 'max': '1400.00', 'avg': '1300.00'})

    def test_get_method_return_404_error(self):
        path = reverse('api:hospital:tracker:app:purchase_price',
                       args=(self.client_1.id, 0, 'entry', 'unit_cost'))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        path = f'/api/clients/{self.client_1.id}/app/categories/{self.category.id}/entry/unknown_cost'
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_method_requires_purchase_price_aggregation(self):
        path = reverse('api:hospital:tracker:app:purchase_price',
                       args=(self.client_1.id, self.category.id, 'advanced', 'unit_cost'))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, {'min': None, 'max': 0, 'avg': 0})

        path = reverse('api:hospital:tracker:app:purchase_price',
                       args=(self.client_1.id, self.category.id, 'entry', 'system_cost'))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, {'min': None, 'max': 0, 'avg': 0})

        entry = ProductLevel.ENTRY.value
        item_1 = ItemFactory(cost_type=SYSTEM_COST, cost=100, is_used=True,
                             device=DeviceFactory(client=self.client_1,
                                                  product=ProductFactory(category=self.category, level=entry)))
        item_2 = ItemFactory(cost_type=SYSTEM_COST, cost=203, is_used=True,
                             device=DeviceFactory(client=self.client_1,
                                                  product=ProductFactory(category=self.category, level=entry)))
        item_3 = ItemFactory(device=DeviceFactory(client=self.client_1), cost_type=UNIT_COST, cost=100, is_used=True)
        RepCaseFactory(procedure_date=datetime.utcnow().date(), items=[item_1, item_2])
        RepCaseFactory(procedure_date=datetime.utcnow().date(), items=[item_3])
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, {
            'min': '100.00',
            'max': '200.00',
            'avg': '151.50'
        })


class PhysicianCategoryListViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.client_1 = ClientFactory()
        physician = AccountFactory(client=self.client_1, user=self.user,
                                   role=RoleFactory(priority=RolePriority.PHYSICIAN.value))
        self.category_1, self.category_2, self.category_3 = CategoryFactory.create_batch(3)
        device_1 = DeviceFactory(client=self.client_1, product=ProductFactory(category=self.category_1))
        device_2 = DeviceFactory(client=self.client_1, product=ProductFactory(category=self.category_2))
        device_3 = DeviceFactory(client=self.client_1, product=ProductFactory(category=self.category_3))
        rep_case = RepCaseFactory(client=self.client_1, physician=physician)
        ItemFactory(device=device_1, rep_case=rep_case, is_used=True)
        ItemFactory(device=device_2, rep_case=rep_case, is_used=True)
        ItemFactory(device=device_3, rep_case=RepCaseFactory(), is_used=True)
        self.path = reverse('api:hospital:tracker:app:categories', args=(self.client_1.id,))

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/clients/{self.client_1.id}/app/categories')

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_get_method_return_list_categories_of_devices_used_by_physician(self):
        response = self.authorized_client.get(self.path)
        self.assertCountEqual(response.data, [
            {
                'id': self.category_1.id,
                'name': self.category_1.name,
                'image': None,
                'parent_id': None,
            },
            {
                'id': self.category_2.id,
                'name': self.category_2.name,
                'image': None,
                'parent_id': None,
            },
        ])

    def test_get_method_return_403_permission_denied(self):
        path = reverse('api:hospital:tracker:app:categories', args=(ClientFactory().id,))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {'detail': 'Unauthorized physician access'})


class PhysicianAPPViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.client_1 = ClientFactory()
        self.category = CategoryFactory()
        self.physician = AccountFactory(client=self.client_1, user=self.user,
                                        role=RoleFactory(priority=RolePriority.PHYSICIAN.value))
        self.path = reverse('api:hospital:tracker:app:physician_app',
                            args=(self.client_1.id, self.category.id, 'entry', 'unit_cost'))

    def test_api_path(self):
        self.assertEqual(self.path,
                         f'/api/clients/{self.client_1.id}/app/categories/{self.category.id}/entry/unit_cost/physician')

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_get_method_returns_empty_physician_app(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {
            'client': {'id': self.client_1.id, 'name': self.client_1.name, 'min': None, 'max': '0.00', 'app': '0.00'},
            'physician': None,
            'manufacturers': []
        })

    @override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
    def test_get_method_returns_physician_app_on_used_devices(self):
        manufacturer = ManufacturerFactory(image=ImageField(filename='medtronic.png'), short_name='MDT')
        entry_device_1 = DeviceFactory(client=self.client_1,
                                       product=ProductFactory(category=self.category,
                                                              level=ProductLevel.ENTRY.value,
                                                              manufacturer=manufacturer))
        entry_device_2 = DeviceFactory(client=self.client_1,
                                       product=ProductFactory(category=self.category, level=ProductLevel.ENTRY.value))
        advanced_device = DeviceFactory(client=self.client_1,
                                        product=ProductFactory(category=self.category,
                                                               level=ProductLevel.ADVANCED.value))
        today = datetime.utcnow().date()
        RepCaseFactory(physician=self.physician, client=self.client_1, procedure_date=today, items=[
            ItemFactory(is_used=True, device=entry_device_1, cost_type=UNIT_COST, cost=100),
            ItemFactory(is_used=True, device=advanced_device, cost_type=UNIT_COST, cost=200),
            ItemFactory(is_used=True, device=entry_device_2, cost_type=UNIT_COST, cost=350),
            ItemFactory(is_used=True, device=advanced_device, cost_type=SYSTEM_COST, cost=470),
        ])
        RepCaseFactory(client=self.client_1, procedure_date=today, items=[
            ItemFactory(is_used=True, device=entry_device_1, cost_type=UNIT_COST, cost=90),
            ItemFactory(is_used=True, device=advanced_device, cost_type=SYSTEM_COST, cost=430),
        ])
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data.pop('manufacturers'), [{
            'id': manufacturer.id,
            'name': 'MDT',
            'app': '100.00',
            'image': 'manufacturers/medtronic.png'
        }, {
            'id': entry_device_2.product.manufacturer.id,
            'name': entry_device_2.product.manufacturer.display_name,
            'app': '350.00',
            'image': None
        }])
        self.assertDictEqual(response.data, {
            'client': {
                'id': self.client_1.id,
                'name': self.client_1.name,
                'min': '90.00',
                'max': '350.00',
                'app': '180.00',
            },
            'physician': {
                'id': self.physician.id,
                'name': self.physician.user.name,
                'app': '225.00',
            },
        })
        rmtree(settings.MEDIA_ROOT)


class PhysicianSavingViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.client_1 = ClientFactory()
        self.today = datetime.utcnow().date()
        self.path = reverse('api:hospital:tracker:saving_by_date',
                            args=(self.client_1.id, '2017-08'))
        physician = AccountFactory(user=self.user, client=self.client_1,
                                   role=RoleFactory(priority=RolePriority.PHYSICIAN.value))
        device_1 = DeviceFactory(client=self.client_1)
        self.item_1, self.item_2 = ItemFactory.create_batch(2, device=device_1, saving=200, cost=1000)
        RepCaseFactory(client=self.client_1, physician=physician, items=[self.item_1, self.item_2],
                       procedure_date=date(2017, 8, 1))
        device_2 = DeviceFactory(client=self.client_1)
        self.item_3 = ItemFactory(device=device_2, saving=150, cost=1000)
        RepCaseFactory(client=self.client_1, physician=physician, items=[self.item_3],
                       procedure_date=date(2017, 7, 5))

        self.item_4 = ItemFactory(device=device_2, saving=200, cost=900)
        RepCaseFactory(client=self.client_1, items=[self.item_4], procedure_date=date(2015, 1, 1))

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/clients/{self.client_1.id}/saving/2017-08')

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_return_saving_at_specify_procedure_date(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.maxDiff = None
        self.assertDictEqual(response.data[0], {
            'name': f'August 2017 savings',
            'client': Decimal('400.00'),
            'physician': Decimal('400.00'),
        })

        year_to_date_savings = response.data[1]
        self.assertCountEqual(year_to_date_savings.pop('categories'), [{
            'id': self.item_1.device.product.category.id,
            'name': self.item_1.device.product.category.name,
            'saving': '400.00',
            'percent': '20.00',
        }, {
            'id': self.item_3.device.product.category.id,
            'name': self.item_3.device.product.category.name,
            'saving': '150.00',
            'percent': '15.00',
        }])
        self.assertDictEqual(year_to_date_savings, {
            'name': f'2017 savings',
            'client': Decimal('550.00'),
            'physician': Decimal('550.00'),
        })

    def test_return_empty_saving_with_procedure_date_in_previous_year(self):
        path = reverse('api:hospital:tracker:saving_by_date', args=(self.client_1.id, '2016-12'))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [{
            'name': f'December 2016 savings',
            'client': None,
            'physician': None,
        }, {
            'name': '2016 savings',
            'client': None,
            'physician': None,
            'categories': [],
        }])

    def test_return_current_month_saving_with_invalid_procedure_date(self):
        path = reverse('api:hospital:tracker:saving', args=(self.client_1.id,))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [{
            'name': f'{month_name[self.today.month]} {self.today.year} savings',
            'client': None,
            'physician': None,
        }, {
            'name': f'{self.today.year} savings',
            'client': None,
            'physician': None,
            'categories': [],
        }])

    def test_return_empty_physician_saving(self):
        path = reverse('api:hospital:tracker:saving_by_date', args=(self.client_1.id, '2015-01'))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.maxDiff = None
        self.assertCountEqual(response.data, [{
            'name': f'January 2015 savings',
            'client': Decimal('200.00'),
            'physician': None,
        }, {
            'name': f'2015 savings',
            'client': Decimal('200.00'),
            'physician': None,
            'categories': [],
        }])
