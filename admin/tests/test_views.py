from datetime import datetime, date, timedelta

from django.urls import reverse
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from rest_framework import status
from rest_framework.test import APITestCase
from faker import Faker

from api.tests.base import APIViewTestCase
from device.factories import ProductFactory, CategoryFactory, SpecialtyFactory, ManufacturerFactory
from hospital.factories import ClientFactory, DeviceFactory, ItemFactory
from order.factories import OrderFactory


from account.factories import UserFactory
from hospital.constants import RolePriority, BULK_PURCHASE, CONSIGNMENT_PURCHASE
from hospital.factories import AccountFactory, RoleFactory
from tracker.factories import RepCaseFactory


class AdminLoginAPIViewTestCase(APITestCase):
    def setUp(self):
        self.path = reverse('api:admin:login')
        self.user = UserFactory(email='admin@neptune.com', name='Dr. Admin')

    def test_api_path(self):
        self.assertEqual(self.path, '/api/admin/login')

    def test_get_method_not_allowed(self):
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_method_empty_data(self):
        response = self.client.post(self.path, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {'detail': 'Email address and password are required.'})

    def test_post_method_with_invalid_data(self):
        response = self.client.post(self.path, {'email': 'admin@neptune.com', 'password': 'wrong password'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {'detail': 'Invalid email/password.'})

    def test_post_method_with_valid_data(self):
        self.assertEqual(AuthToken.objects.count(), 0)

        AccountFactory(user=self.user, role=RoleFactory(priority=RolePriority.PHYSICIAN.value))
        response = self.client.post(self.path, {'email': 'admin@neptune.com', 'password': 'password1'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': 'Unauthorized admin access'})

        admin_client = AccountFactory(user=self.user, role=RoleFactory(priority=RolePriority.ADMIN.value)).client
        for token_count in range(1, 3):
            AccountFactory(user=self.user, role=RoleFactory(priority=RolePriority.ADMIN.value))
            response = self.client.post(self.path, {'email': 'admin@neptune.com', 'password': 'password1'})
            response_data = response.data

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            token = response_data.pop('token')
            self.assertDictEqual(response_data, {
                'user': {
                    'email': 'admin@neptune.com',
                    'name': 'Dr. Admin',
                    'default_client': None,
                    'admin_client': {'id': admin_client.id, 'name': admin_client.name, 'image': None}
                }
            })
            self.assertIsNotNone(token)
            self.assertEqual(AuthToken.objects.count(), token_count)

            user, auth_token = TokenAuthentication().authenticate_credentials(token.encode())
            self.assertEqual(user, self.user)

        self.assertEqual(AuthToken.objects.filter(user=self.user).count(), 2)


class OrderSummaryBySpecialtyListAPIView(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.admin = AccountFactory.create(role=RoleFactory(priority=RolePriority.ADMIN.value),
                                           user=self.user)
        self.specialty_1, self.specialty_2, self.specialty_3 = SpecialtyFactory.create_batch(3)

        self.category_1 = CategoryFactory(specialty=self.specialty_1)
        self.category_2 = CategoryFactory(specialty=self.specialty_2)
        self.category_3 = CategoryFactory(specialty=self.specialty_2)
        self.category_4 = CategoryFactory(specialty=self.specialty_3)

        self.product_1 = ProductFactory(category=self.category_1)
        self.product_2 = ProductFactory(category=self.category_2)
        self.product_3 = ProductFactory(category=self.category_3)
        self.product_4 = ProductFactory(category=self.category_4)

        faker = Faker()
        self.category_1_orders = faker.random_int(min=1, max=20)
        self.category_2_orders = faker.random_int(min=1, max=20)
        self.category_3_orders = faker.random_int(min=1, max=20)
        self.specialty_1_orders = self.category_1_orders
        self.specialty_2_orders = self.category_2_orders + self.category_3_orders
        self.total_num_orders = self.specialty_1_orders + self.specialty_2_orders

        OrderFactory.create_batch(self.category_1_orders,
                                  physician=AccountFactory(client=self.admin.client),
                                  product=self.product_1)
        OrderFactory.create_batch(self.category_2_orders,
                                  physician=AccountFactory(client=self.admin.client),
                                  product=self.product_2)
        OrderFactory.create_batch(self.category_3_orders,
                                  physician=AccountFactory(client=self.admin.client),
                                  product=self.product_3)
        self.path = reverse('api:admin:ordersummary_by_specialty', args=(self.admin.client.id,))

    def test_api_path(self):
        self.assertEqual(
            self.path, f'/api/admin/clients/{self.admin.client.id}/ordersummary')

    def test_view_order_of_other_client(self):
        client = ClientFactory()
        path = reverse('api:admin:ordersummary_by_specialty', args=(client.id,))

        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {'detail': 'Unauthorized admin access'})

        AccountFactory(client=client, user=self.user, role=RoleFactory(priority=RolePriority.PHYSICIAN.value))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {'detail': 'Unauthorized admin access'})

    def test_view_their_client_order(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data['client'], {
            'id': self.admin.client.id,
            'name': self.admin.client.name,
            'count': self.total_num_orders
        })
        self.assertCountEqual(response.data['specialties'], [
            {'id': self.specialty_1.id, 'name': self.specialty_1.name, 'count': self.specialty_1_orders},
            {'id': self.specialty_2.id, 'name': self.specialty_2.name, 'count': self.specialty_2_orders}
        ])

    def test_client_without_any_order(self):
        client_admin = AccountFactory(role=RoleFactory(priority=RolePriority.ADMIN.value), user=self.user)
        path = reverse('api:admin:ordersummary_by_specialty', args=(client_admin.client.id,))

        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['client']['count'], 0)
        self.assertCountEqual(response.data['specialties'], [])


class ClientMarketshareViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.client_1 = ClientFactory()
        self.manufacturer_1, self.manufacturer_2 = ManufacturerFactory.create_batch(2)
        AccountFactory(client=self.client_1, role=RoleFactory(priority=RolePriority.ADMIN.value), user=self.user)
        self.path = reverse('api:admin:marketshare', args=(self.client_1.id,))

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/admin/clients/{self.client_1.id}/marketshare')

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_get_method_return_403_error(self):
        client = ClientFactory()
        path = reverse('api:admin:marketshare', args=(client.id,))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': 'Unauthorized admin access'})

    def test_return_empty_client_marketshare(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {
            'name': f'{datetime.utcnow().year} Year to Date',
            'marketshare': [],
        })

    def test_return_client_marketshare_for_current_year(self):
        current_year = datetime.utcnow().year
        client_2 = ClientFactory()
        device = DeviceFactory(client=self.client_1, product=ProductFactory(manufacturer=self.manufacturer_1))
        device_2 = DeviceFactory(client=self.client_1, product=ProductFactory(manufacturer=self.manufacturer_2))
        device_3 = DeviceFactory(client=client_2, product=ProductFactory(manufacturer=self.manufacturer_1))
        item_1, item_2 = ItemFactory.create_batch(2, device=device)
        item_3, item_4, item_5 = ItemFactory.create_batch(3, device=device_2)
        item_6 = ItemFactory(device=device_3)
        RepCaseFactory(client=self.client_1, items=[item_1, item_3], procedure_date=date(current_year, 5, 1))
        RepCaseFactory(client=self.client_1, items=[item_2, item_4], procedure_date=date(current_year, 4, 30))
        RepCaseFactory(client=self.client_1, items=[item_5], procedure_date=date(current_year - 1, 4, 30))
        RepCaseFactory(client=client_2, items=[item_6], procedure_date=date(current_year, 5, 1))

        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {
            'name': f'{current_year} Year to Date',
            'marketshare': [{
                'spend': f'{(item_1.cost + item_2.cost):.2f}', 'units': 2,
                'name': self.manufacturer_1.display_name, 'id': self.manufacturer_1.id,
            }, {
                'spend': f'{(item_3.cost + item_4.cost):.2f}', 'units': 2,
                'name': self.manufacturer_2.display_name, 'id': self.manufacturer_2.id,
            }],
        })


class TodayCasesAPIViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.client_1 = ClientFactory()
        AccountFactory(client=self.client_1, role=RoleFactory(priority=RolePriority.ADMIN.value), user=self.user)
        today = datetime.utcnow().date()
        product_1 = ProductFactory(
            name='Etrinsa',
            manufacturer=ManufacturerFactory(name='Biotronik'),
            category=CategoryFactory(name='VVI Pacemakers'),
            model_number='394936',
        )
        product_2 = ProductFactory(
            name='Resolute Integrity',
            manufacturer=ManufacturerFactory(short_name='MDT', name='Medtronic'),
            category=CategoryFactory(name='Drug Eluting'),
            model_number='82940',
        )
        device_1 = DeviceFactory(product=product_1, client=self.client_1)
        device_2 = DeviceFactory(product=product_2, client=self.client_1)
        physician = AccountFactory(user=UserFactory(name='Val Vular'))
        rep_case = RepCaseFactory(procedure_date=today, physician=physician)
        self.item_1 = ItemFactory(rep_case=rep_case, device=device_1, serial_number='SER01')
        self.item_2 = ItemFactory(rep_case=rep_case, device=device_2, serial_number='sensia')
        ItemFactory(device=device_1, rep_case=RepCaseFactory(procedure_date=datetime(2018, 8, 9)))
        self.path = reverse('api:admin:today_cases', args=(self.client_1.id,))

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/admin/clients/{self.client_1.id}/cases')

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_get_method_return_403_error(self):
        other_client = ClientFactory()
        path = reverse('api:admin:today_cases', args=(other_client.id,))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': 'Unauthorized admin access'})

    def test_return_today_cases(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.maxDiff = None
        self.assertCountEqual(response.data, [{
            'id': self.item_1.id,
            'identifier': 'SER01',
            'purchase_type': 'Bulk',
            'physician': 'Val Vular',
            'manufacturer': 'Biotronik',
            'category': 'VVI Pacemakers',
            'product': 'Etrinsa',
            'model_number': '394936',
        }, {
            'id': self.item_2.id,
            'identifier': 'sensia',
            'purchase_type': 'Bulk',
            'physician': 'Val Vular',
            'manufacturer': 'MDT',
            'category': 'Drug Eluting',
            'product': 'Resolute Integrity',
            'model_number': '82940',
        }])


class SavingsAPIViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.client_1 = ClientFactory()
        AccountFactory(client=self.client_1, role=RoleFactory(priority=RolePriority.ADMIN.value), user=self.user)
        current_year = datetime.utcnow().year
        self.previous_year = current_year - 1
        rep_case_1 = RepCaseFactory(procedure_date=date(current_year, 1, 2), client=self.client_1)
        rep_case_2 = RepCaseFactory(procedure_date=date(current_year, 4, 2), client=self.client_1)
        rep_case_3 = RepCaseFactory(procedure_date=date(current_year, 8, 2), client=self.client_1)
        ItemFactory(rep_case=rep_case_1, saving=200, cost=1000)
        ItemFactory(rep_case=rep_case_2, saving=300, cost=2000)
        ItemFactory(rep_case=rep_case_2, saving=200, cost=3000)
        ItemFactory(rep_case=rep_case_3, saving=100, cost=4000)

        rep_case_4 = RepCaseFactory(procedure_date=date(self.previous_year, 3, 2), client=self.client_1)
        rep_case_5 = RepCaseFactory(procedure_date=date(self.previous_year, 7, 2), client=self.client_1)
        ItemFactory(rep_case=rep_case_4, saving=100, cost=1000)
        ItemFactory(rep_case=rep_case_4, saving=200, cost=1000)
        ItemFactory(rep_case=rep_case_5, saving=300, cost=3000)

        self.path = reverse('api:admin:savings', args=(self.client_1.id,))
        self.path_with_year = reverse('api:admin:savings_by_year', args=(self.client_1.id, self.previous_year))

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/admin/clients/{self.client_1.id}/savings')

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_return_year_to_date_savings(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [
            {
                'month': 1,
                'savings': '200.00',
                'spend': '1000.00',
                'percent': '20.00',
            },
            {
                'month': 4,
                'savings': '500.00',
                'spend': '5000.00',
                'percent': '10.00',
            },
            {
                'month': 8,
                'savings': '100.00',
                'spend': '4000.00',
                'percent': '2.50',
            }
        ])

    def test_api_path_with_year_argument(self):
        self.assertEqual(self.path_with_year, f'/api/admin/clients/{self.client_1.id}/savings/{self.previous_year}')

    def test_get_with_year_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user(self.path_with_year)

    def test_return_savings_for_a_year(self):
        response = self.authorized_client.get(self.path_with_year)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [
            {
                'month': 3,
                'savings': '300.00',
                'spend': '2000.00',
                'percent': '15.00',
            },
            {
                'month': 7,
                'savings': '300.00',
                'spend': '3000.00',
                'percent': '10.00',
            },
        ])


class BulkAPIViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.client_1 = ClientFactory()
        AccountFactory(client=self.client_1, role=RoleFactory(priority=RolePriority.ADMIN.value), user=self.user)
        self.path = reverse('api:admin:bulk', args=(self.client_1.id,))

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/admin/clients/{self.client_1.id}/bulk')

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_return_bulk_inventory_info(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {
            'available': 0,
            'expiring60': 0,
            'expiring30': 0,
            'expired': 0,
        })

        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        ItemFactory(purchase_type=BULK_PURCHASE, expired_date=today)
        ItemFactory(purchase_type=BULK_PURCHASE, expired_date=yesterday)
        ItemFactory.create_batch(2, purchase_type=BULK_PURCHASE, expired_date=today + timedelta(days=15))
        ItemFactory.create_batch(5, purchase_type=BULK_PURCHASE, expired_date=today + timedelta(days=30))
        ItemFactory.create_batch(3, purchase_type=BULK_PURCHASE, expired_date=today + timedelta(days=60))
        ItemFactory.create_batch(4, purchase_type=BULK_PURCHASE, expired_date=today + timedelta(days=70))
        ItemFactory.create_batch(3, purchase_type=BULK_PURCHASE, expired_date=today + timedelta(days=20), is_used=True)
        ItemFactory.create_batch(3, purchase_type=CONSIGNMENT_PURCHASE, expired_date=today + timedelta(days=20))
        self.assertCountEqual(response.data, {
            'available': 16,    # total
            'expiring60': 5,    # 5
            'expiring30': 3,    # today + 2
            'expired': 1,       # yesterday
        })


class PhysiciansAPIViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.client_1 = ClientFactory()
        AccountFactory(client=self.client_1, role=RoleFactory(priority=RolePriority.ADMIN.value), user=self.user)

        self.path = reverse('api:admin:physicians', args=(self.client_1.id,))

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/admin/clients/{self.client_1.id}/physicians')

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_get_method_return_403_error(self):
        client = ClientFactory()
        path = reverse('api:admin:physicians', args=(client.id,))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': 'Unauthorized admin access'})

    def test_return_physicians_of_the_client(self):
        AccountFactory.create_batch(3)
        physician_1, physician_2 = AccountFactory.create_batch(2, client=self.client_1,
                                                               role=RoleFactory(priority=RolePriority.PHYSICIAN.value))
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [{
            'id': physician_1.id,
            'name': physician_1.user.name,
            'email': physician_1.user.email,
        }, {
            'id': physician_2.id,
            'name': physician_2.user.name,
            'email': physician_2.user.email,
        }])


class SpecialtiesAPIView(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.client_1 = ClientFactory()
        AccountFactory(client=self.client_1, role=RoleFactory(priority=RolePriority.ADMIN.value), user=self.user)

        self.specialty_1, self.specialty_2, self.specialty_3 = SpecialtyFactory.create_batch(3)

        self.category_1 = CategoryFactory(specialty=self.specialty_1)
        self.category_2 = CategoryFactory(specialty=self.specialty_2)
        self.category_3 = CategoryFactory(specialty=self.specialty_2)
        self.category_4 = CategoryFactory(specialty=self.specialty_3)

        device_1 = DeviceFactory(client=self.client_1, product=ProductFactory(category=self.category_1))
        device_2 = DeviceFactory(client=self.client_1, product=ProductFactory(category=self.category_2))
        DeviceFactory(client=self.client_1, product=ProductFactory(category=self.category_3))
        DeviceFactory(client=self.client_1, product=ProductFactory(category=self.category_4))

        ItemFactory.create_batch(2, device=device_1)
        ItemFactory.create_batch(3, device=device_2)

        self.path = reverse('api:admin:specialties', args=(self.client_1.id,))

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/admin/clients/{self.client_1.id}/specialties')

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_get_method_return_403_error(self):
        other_client = ClientFactory()
        path = reverse('api:admin:specialties', args=(other_client.id,))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': 'Unauthorized admin access'})

    def test_return_specialties_of_the_client(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [{
            'id': self.specialty_1.id,
            'name': self.specialty_1.name,
        }, {
            'id': self.specialty_2.id,
            'name': self.specialty_2.name,
        }])
