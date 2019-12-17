from calendar import month_name
from datetime import datetime, date
from decimal import Decimal

from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from factory.django import ImageField
from rest_framework import status
from shutil import rmtree

from api.tests.base import APIViewTestCase
from device.factories import CategoryFactory, ProductFactory, FeatureFactory, CategoryFeatureFactory, \
    ManufacturerFactory
from hospital.factories import AccountFactory, ClientFactory, DeviceFactory, ItemFactory, RoleFactory
from hospital.constants import CONSIGNMENT_PURCHASE, BULK_PURCHASE, RolePriority
from neptune.factories import SharedImageFactory
from price.constants import ON_DOCTOR_ORDER, PRE_DOCTOR_ORDER
from price.factories import ClientPriceFactory, DiscountFactory
from price.constants import VALUE_DISCOUNT, UNIT_COST, PERCENT_DISCOUNT, SYSTEM_COST
from tracker.factories import RepCaseFactory


class CategoryListViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.category_1, self.category_2 = CategoryFactory.create_batch(2)
        self.client_1, self.client_2 = ClientFactory.create_batch(2)
        self.user.default_client = self.client_1
        self.user.save()
        self.path = reverse('api:hospital:device:categories', args=(self.client_1.id,))
        self.account_1 = AccountFactory.create(user=self.user, client=self.client_1)
        self.account_2 = AccountFactory.create(user=self.user, client=self.client_2)
        ClientPriceFactory(client=self.client_1, product=ProductFactory(category=self.category_1))
        ClientPriceFactory(client=self.client_1, product=ProductFactory(category=self.category_2))
        ClientPriceFactory(client=self.client_2, product=ProductFactory(category=self.category_1))
        ClientPriceFactory.create_batch(3)

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/clients/{self.client_1.id}/categories')

    def test_get_method_authenticated_user_return_list_categories(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        self.account_1.specialties.add(self.category_1.specialty)
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [
            {'id': self.category_1.id, 'name': self.category_1.name, 'image': None, 'parent_id': None},
        ])

        self.account_1.specialties.add(self.category_2.specialty)
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [
            {'id': self.category_1.id, 'name': self.category_1.name, 'image': None, 'parent_id': None},
            {'id': self.category_2.id, 'name': self.category_2.name, 'image': None, 'parent_id': None}
        ])

        path = reverse('api:hospital:device:categories', args=(self.client_2.id,))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        self.account_2.specialties.set([self.category_1.specialty, self.category_2.specialty])
        parent_category = CategoryFactory()
        self.category_1.parent = parent_category
        self.category_1.save()
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [
            {'id': self.category_1.id, 'name': self.category_1.name, 'image': None, 'parent_id': parent_category.id},
            {'id': parent_category.id, 'name': parent_category.name, 'image': None, 'parent_id': None},
        ])

    def test_get_method_with_client_does_not_contain_user(self):
        client = ClientFactory()
        path = reverse('api:hospital:device:categories', args=(client.id,))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class ProductListViewTestCase(APIViewTestCase):
    def tearDown(self):
        super().tearDown()
        rmtree(settings.MEDIA_ROOT)

    def setUp(self):
        super().setUp()
        self.category = CategoryFactory()
        self.client_1 = ClientFactory()
        AccountFactory.create(user=self.user, client=self.client_1)
        self.product_1, self.product_2 = ProductFactory.create_batch(2, category=self.category)
        self.feature_1 = FeatureFactory(name='Wireless', product=self.product_2,
                                        shared_image=SharedImageFactory(image=ImageField(filename='wireless.jpg')))
        self.feature_2, self.feature_3 = FeatureFactory.create_batch(2, product=self.product_2)
        price_1 = ClientPriceFactory(client=self.client_1, product=self.product_1, unit_cost=200, system_cost=300)
        price_2 = ClientPriceFactory(client=self.client_1, product=self.product_2, unit_cost=250, system_cost=300)
        ClientPriceFactory(client=self.client_1, unit_cost=250, system_cost=300,
                           product=ProductFactory(enabled=False),)
        self.discount_1 = DiscountFactory(
            client_price=price_1, discount_type=VALUE_DISCOUNT, value=50, name='CCO', order=1, percent=0,
            apply_type=ON_DOCTOR_ORDER, cost_type=UNIT_COST,
            shared_image=SharedImageFactory(image=ImageField(filename='CCO.png'))
        )
        self.discount_2 = DiscountFactory(
            client_price=price_2, discount_type=PERCENT_DISCOUNT, percent=10, cost_type=SYSTEM_COST, order=2,
            apply_type=ON_DOCTOR_ORDER, name='Repless',
            shared_image=SharedImageFactory(image=ImageField(filename='repless.png'))
        )
        self.discount_3 = DiscountFactory(
            client_price=price_1, discount_type=PERCENT_DISCOUNT, value=0, name='Bulk', order=2, percent=15,
            apply_type=PRE_DOCTOR_ORDER, cost_type=UNIT_COST, shared_image=None)
        device = self.client_1.device_set.get(product=self.product_1)
        ItemFactory(device=device, discounts=[self.discount_3], purchase_type=BULK_PURCHASE, is_used=False,
                    cost_type=UNIT_COST)

        self.path = reverse('api:hospital:device:products', args=(self.client_1.id, self.category.id,))

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/clients/{self.client_1.id}/categories/{self.category.id}/products')

    def test_get_method_authenticated_user_returns_list_of_enabled_products_with_prices(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        manufacturer_1 = self.product_1.manufacturer
        manufacturer_2 = self.product_2.manufacturer
        expected = [
            {
                'id': self.product_1.id,
                'name': self.product_1.name,
                'image': None,
                'level': self.product_1.level,
                'manufacturer': {
                    'id': manufacturer_1.id,
                    'name': manufacturer_1.name,
                    'short_name': manufacturer_1.short_name,
                    'image': None,
                },
                'model_number': str(self.product_1.model_number),
                'unit_cost': {
                    'value': Decimal(200.00),
                    'discounts': [{
                        'id': self.discount_1.id, 'name': 'CCO', 'value': '50.00', 'order': 1,
                        'image': 'shared/CCO.png', 'percent': '0.00', 'discount_type': VALUE_DISCOUNT,
                        'apply_type': ON_DOCTOR_ORDER
                    }, {
                        'id': self.discount_3.id, 'name': 'Bulk', 'value': '0.00', 'order': 2,
                        'image': None, 'percent': '15.00', 'discount_type': PERCENT_DISCOUNT,
                        'apply_type': PRE_DOCTOR_ORDER
                    }],
                },
                'system_cost': {
                    'value': Decimal(300.00),
                    'discounts': [],
                },
                'bulk': 1,
                'features': [],
            },
            {
                'id': self.product_2.id,
                'name': self.product_2.name,
                'image': None,
                'level': self.product_2.level,
                'manufacturer': {
                    'id': manufacturer_2.id,
                    'name': manufacturer_2.name,
                    'short_name': manufacturer_2.short_name,
                    'image': None,
                },
                'model_number': str(self.product_2.model_number),
                'unit_cost': {
                    'value': Decimal(250.00),
                    'discounts': [],
                },
                'system_cost': {
                    'value': Decimal(300.00),
                    'discounts': [{
                        'id': self.discount_2.id, 'name': 'Repless', 'value': '0.00',
                        'order': 2, 'image': 'shared/repless.png', 'percent': '10.00',
                        'discount_type': PERCENT_DISCOUNT, 'apply_type': ON_DOCTOR_ORDER
                    }],
                },
                'bulk': 0,
                'features': [{
                    'id': self.feature_1.id,
                    'name': 'Wireless',
                    'value': self.feature_2.value,
                    'image': 'shared/wireless.jpg',
                    'category_feature': self.feature_1.category_feature.id,
                }, {
                    'id': self.feature_2.id,
                    'name': self.feature_2.name,
                    'value': self.feature_2.value,
                    'image': None,
                    'category_feature': self.feature_2.category_feature.id,
                }, {
                    'id': self.feature_3.id,
                    'name': self.feature_3.name,
                    'value': self.feature_3.value,
                    'image': None,
                    'category_feature': self.feature_3.category_feature.id,
                }],
            },
        ]
        self.assertCountEqual(response.data, expected)

    def test_get_method_with_client_does_not_contain_user(self):
        client = ClientFactory()
        path = reverse('api:hospital:device:products', args=(client.id, self.category.id,))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ItemListViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.client_1 = ClientFactory()
        self.product = ProductFactory()
        self.path = reverse('api:hospital:device:items', args=(self.client_1.id, self.product.id))
        AccountFactory(client=self.client_1, user=self.user)
        ItemFactory.create_batch(2, device=DeviceFactory(product=self.product))
        ItemFactory(device=DeviceFactory(client=self.client_1))
        device = DeviceFactory(client=self.client_1, product=self.product)
        self.item_1, self.item_2 = ItemFactory.create_batch(2, device=device, is_used=False,
                                                            purchase_type=BULK_PURCHASE)
        ItemFactory(device=device, purchase_type=CONSIGNMENT_PURCHASE, is_used=False)
        ItemFactory(device=device, purchase_type=BULK_PURCHASE, is_used=True)

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/clients/{self.client_1.id}/products/{self.product.id}/items')

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_get_method_return_404_error(self):
        client = ClientFactory()
        path = reverse('api:hospital:device:items', args=(client.id, self.product.id))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        product = ProductFactory()
        path = reverse('api:hospital:device:items', args=(self.client_1.id, product.id))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_method_with_authorized_user_returns_unsused_items_purchased_in_bulk(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertCountEqual(response.data, [
            {
                'identifier': self.item_1.identifier,
                'expired_date': str(self.item_1.expired_date),
                'purchased_date': str(self.item_1.purchased_date),
            },
            {
                'identifier': self.item_2.identifier,
                'expired_date': str(self.item_2.expired_date),
                'purchased_date': str(self.item_2.purchased_date),
            },
        ])


class PhysicianMarketshareViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.client_1 = ClientFactory()
        self.today = datetime.utcnow().date()
        self.manufacturer_1, self.manufacturer_2 = ManufacturerFactory.create_batch(2)
        self.physician = AccountFactory(client=self.client_1, role=RoleFactory(priority=RolePriority.PHYSICIAN.value),
                                        user=self.user)
        self.path = reverse('api:hospital:device:marketshare', args=(self.client_1.id,))

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/clients/{self.client_1.id}/marketshare')
        this_month = f'{self.today.year}-{self.today.month}'
        self.assertEqual(
            reverse('api:hospital:device:marketshare_by_date', args=(self.client_1.id, this_month)),
            f'/api/clients/{self.client_1.id}/marketshare/{this_month}'
        )

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_get_method_return_404_error(self):
        client = ClientFactory()
        path = reverse('api:hospital:device:marketshare', args=(client.id,))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_return_marketshare_without_specify_procedure_date(self):
        device = DeviceFactory(client=self.client_1, product=ProductFactory(manufacturer=self.manufacturer_1))
        item_1, item_2 = ItemFactory.create_batch(2, device=device)
        RepCaseFactory(client=self.client_1, physician=self.physician, items=[item_1, item_2],
                       procedure_date=self.today)

        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [
            {
                'name': f'{month_name[self.today.month]}, {self.today.year}',
                'marketshare': [
                    {
                        'spend': f'{(item_1.cost + item_2.cost):.2f}',
                        'units': 2,
                        'name': self.manufacturer_1.display_name,
                        'id': self.manufacturer_1.id,
                    },
                ],
            }, {
                'name': f'{self.today.year} to Date',
                'marketshare': [
                    {
                        'spend': f'{(item_1.cost + item_2.cost):.2f}',
                        'units': 2,
                        'name': self.manufacturer_1.display_name,
                        'id': self.manufacturer_1.id,
                    },
                ],
            }
        ])

    def test_return_marketshare_with_procedure_date(self):
        device = DeviceFactory(client=self.client_1, product=ProductFactory(manufacturer=self.manufacturer_1))
        device_2 = DeviceFactory(client=self.client_1, product=ProductFactory(manufacturer=self.manufacturer_2))
        item_1, item_2 = ItemFactory.create_batch(2, device=device)
        item_3, item_4 = ItemFactory.create_batch(2, device=device_2)
        RepCaseFactory(client=self.client_1, physician=self.physician, items=[item_1, item_3],
                       procedure_date=date(2018, 5, 1))
        RepCaseFactory(client=self.client_1, physician=self.physician, items=[item_2, item_4],
                       procedure_date=date(2018, 4, 30))

        path = reverse('api:hospital:device:marketshare_by_date', args=(self.client_1.id, '2018-5'))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [
            {
                'name': 'May, 2018',
                'marketshare': [{
                    'spend': f'{item_1.cost:.2f}', 'units': 1,
                    'name': self.manufacturer_1.display_name, 'id': self.manufacturer_1.id,
                }, {
                    'spend': f'{item_3.cost:.2f}', 'units': 1,
                    'name': self.manufacturer_2.display_name, 'id': self.manufacturer_2.id,
                }],
            }, {
                'name': f'2018 to Date',
                'marketshare': [{
                    'spend': f'{(item_1.cost + item_2.cost):.2f}', 'units': 2,
                    'name': self.manufacturer_1.display_name, 'id': self.manufacturer_1.id,
                }, {
                    'spend': f'{(item_3.cost + item_4.cost):.2f}', 'units': 2,
                    'name': self.manufacturer_2.display_name, 'id': self.manufacturer_2.id,
                }],
            }
        ])

        path = reverse('api:hospital:device:marketshare_by_date', args=(self.client_1.id, '2018-04'))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [
            {
                'name': 'April, 2018',
                'marketshare': [{
                    'spend': f'{item_2.cost:.2f}', 'units': 1,
                    'name': self.manufacturer_1.display_name, 'id': self.manufacturer_1.id,
                }, {
                    'spend': f'{item_4.cost:.2f}', 'units': 1,
                    'name': self.manufacturer_2.display_name, 'id': self.manufacturer_2.id,
                }],
            }, {
                'name': f'2018 to Date',
                'marketshare': [{
                    'spend': f'{(item_1.cost + item_2.cost):.2f}', 'units': 2,
                    'name': self.manufacturer_1.display_name, 'id': self.manufacturer_1.id,
                }, {
                    'spend': f'{(item_3.cost + item_4.cost):.2f}', 'units': 2,
                    'name': self.manufacturer_2.display_name, 'id': self.manufacturer_2.id,
                }],
            }
        ])


@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class FeatureListViewTestCase(APIViewTestCase):
    def tearDown(self):
        super().tearDown()
        rmtree(settings.MEDIA_ROOT)

    def setUp(self):
        super().setUp()
        self.product = ProductFactory()
        self.shared_image = SharedImageFactory(name='url', image=ImageField(filename='test_image.jpg'))
        self.category_feature = CategoryFeatureFactory(name='website', category=self.product.category)
        self.feature_1 = FeatureFactory(name='size', value='24/11', product=self.product, category_feature=None)
        self.feature_2 = FeatureFactory(name='website', value='http://biotronik.com', shared_image=self.shared_image,
                                        category_feature=self.category_feature, product=self.product)
        self.feature_3 = FeatureFactory(name='shock', value='yes', shared_image=self.shared_image, product=self.product,
                                        category_feature=None)
        FeatureFactory(product=self.product, value=None)
        self.path = reverse('api:device:features', args=(self.product.id,))

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/products/{self.product.id}/features')

    def test_get_method_return_feature_list(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [
            {
                'id': self.feature_1.id,
                'name': 'size',
                'value': '24/11',
                'image': None,
                'category_feature': self.feature_1.category_feature.id,
            },
            {
                'id': self.feature_2.id,
                'name': 'website',
                'value': 'http://biotronik.com',
                'image': self.shared_image.image.url,
                'category_feature': self.category_feature.id,
            },
            {
                'id': self.feature_3.id,
                'name': 'shock',
                'value': 'yes',
                'image': self.shared_image.image.url,
                'category_feature': self.feature_3.category_feature.id,
            },
        ])

    def test_get_method_return_404_error(self):
        path = reverse('api:device:features', args=(0,))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_method_empty_features_list(self):
        path = reverse('api:device:features', args=(ProductFactory().id,))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
