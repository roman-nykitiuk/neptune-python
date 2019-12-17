from django.urls import reverse
from rest_framework import status

from api.tests.base import StaffAPIViewTestCase
from device.factories import ManufacturerFactory, ProductFactory, CategoryFactory
from hospital.constants import RolePriority
from hospital.factories import ClientFactory, AccountFactory, DeviceFactory, ItemFactory
from price.constants import UNIT_COST, SYSTEM_COST
from price.factories import DiscountFactory, ClientPriceFactory


class ManufacturerEntryListViewTestCase(StaffAPIViewTestCase):
    def setUp(self):
        super().setUp()
        self.manufacturer = ManufacturerFactory()
        self.path = reverse('api:staff:rebatable_items', args=(self.manufacturer.id, 'product'))

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/staff/manufacturers/{self.manufacturer.id}/product')

    def test_token_authorized_staff_user(self):
        self._test_token_authorized_staff_user()

    def test_session_authorized_non_staff_user(self):
        self._test_session_authorized_non_staff_user()

    def test_session_authorized_admin_user(self):
        response = self.authorized_admin_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        product_1, product_2 = ProductFactory.create_batch(2, manufacturer=self.manufacturer)
        product_3 = ProductFactory(category=product_1.category, manufacturer=self.manufacturer)
        ProductFactory(category=CategoryFactory(specialty=product_2.category.specialty))
        response = self.authorized_admin_client.get(self.path)
        self.assertCountEqual(response.data, [
            {'id': product_1.id, 'name': product_1.name},
            {'id': product_2.id, 'name': product_2.name},
            {'id': product_3.id, 'name': product_3.name},
        ])

        path = reverse('api:staff:rebatable_items', args=(self.manufacturer.id, 'category'))
        self.assertEqual(path, f'/api/staff/manufacturers/{self.manufacturer.id}/category')
        response = self.authorized_admin_client.get(path)
        self.assertCountEqual(response.data, [
            {'id': product_1.category.id, 'name': product_1.category.name},
            {'id': product_2.category.id, 'name': product_2.category.name},
        ])

        path = reverse('api:staff:rebatable_items', args=(self.manufacturer.id, 'specialty'))
        self.assertEqual(path, f'/api/staff/manufacturers/{self.manufacturer.id}/specialty')
        response = self.authorized_admin_client.get(path)
        self.assertCountEqual(response.data, [
            {'id': product_1.category.specialty.id, 'name': product_1.category.specialty.name},
            {'id': product_2.category.specialty.id, 'name': product_2.category.specialty.name},
        ])

        path = f'/api/staff/manufacturers/{self.manufacturer.id}/manufacturer'
        response = self.authorized_admin_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AccountListAPIViewTestCase(StaffAPIViewTestCase):
    def setUp(self):
        super().setUp()
        self.hospital = ClientFactory()
        self.account_1, self.account_2 = AccountFactory.create_batch(2, client=self.hospital)
        AccountFactory()
        self.path = reverse('api:staff:accounts', args=(self.hospital.id,))

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/staff/clients/{self.hospital.id}/accounts')

    def test_token_authorized_staff_user(self):
        self._test_token_authorized_staff_user()

    def test_session_authorized_non_staff_user(self):
        self._test_session_authorized_non_staff_user()

    def test_session_authorized_staff_user(self):
        response = self.authorized_admin_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [
            {
                'id': self.account_1.id,
                'name': self.account_1.user.name,
                'email': self.account_1.user.email,
                'is_physician': self.account_1.role.priority == RolePriority.PHYSICIAN.value,
            },
            {
                'id': self.account_2.id,
                'name': self.account_2.user.name,
                'email': self.account_2.user.email,
                'is_physician': self.account_2.role.priority == RolePriority.PHYSICIAN.value,
            },
        ])


class DiscountListAPIViewTestCase(StaffAPIViewTestCase):
    def setUp(self):
        super().setUp()
        self.hospital = ClientFactory()
        self.path = reverse('api:staff:discounts', args=(self.hospital.id,))

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/staff/clients/{self.hospital.id}/discounts')

    def test_token_authorized_staff_user(self):
        self._test_token_authorized_staff_user()

    def test_session_authorized_non_staff_user(self):
        self._test_session_authorized_non_staff_user()

    def test_session_authorized_staff_user(self):
        product_1, product_2 = ProductFactory.create_batch(2)
        discount_1, discount_3 = DiscountFactory.create_batch(2, cost_type=UNIT_COST)
        discount_2 = DiscountFactory(cost_type=SYSTEM_COST)
        ClientPriceFactory(client=self.hospital, product=product_1, discounts=[discount_1])
        ClientPriceFactory(client=self.hospital, product=product_2, discounts=[discount_2, discount_3])
        response = self.authorized_admin_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [
            {
                'id': product_1.id,
                'discounts': {
                    UNIT_COST: [{'id': discount_1.id, 'name': discount_1.name}],
                    SYSTEM_COST: []
                }
            }, {
                'id': product_2.id,
                'discounts': {
                    UNIT_COST: [{'id': discount_3.id, 'name': discount_3.name}],
                    SYSTEM_COST: [{'id': discount_2.id, 'name': discount_2.name}]
                }
            },
        ])


class DeviceListAPIViewTestCase(StaffAPIViewTestCase):
    def setUp(self):
        super().setUp()
        self.hospital = ClientFactory()
        self.path = reverse('api:staff:devices', args=(self.hospital.id,))

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/staff/clients/{self.hospital.id}/devices')

    def test_token_authorized_staff_user(self):
        self._test_token_authorized_staff_user()

    def test_session_authorized_non_staff_user(self):
        self._test_session_authorized_non_staff_user()

    def test_session_authorized_staff_user(self):
        DeviceFactory.create_batch(3)
        device_1, device_2 = DeviceFactory.create_batch(2, client=self.hospital)
        response = self.authorized_admin_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [
            {
                'id': device_1.id,
                'name': device_1.product.name,
                'category': device_1.product.category.name,
                'specialty': device_1.product.category.specialty.name,
                'manufacturer': device_1.product.manufacturer.display_name,
                'product': device_1.product.id,
            },
            {
                'id': device_2.id,
                'name': device_2.product.name,
                'category': device_2.product.category.name,
                'specialty': device_2.product.category.specialty.name,
                'manufacturer': device_2.product.manufacturer.display_name,
                'product': device_2.product.id,
            },
        ])


class ItemListAPIViewTestCase(StaffAPIViewTestCase):
    def setUp(self):
        super().setUp()
        self.hospital = ClientFactory()
        self.device = DeviceFactory(client=self.hospital)
        self.path = reverse('api:staff:items', args=(self.device.id,))

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/staff/devices/{self.device.id}/items')

    def test_token_authorized_staff_user(self):
        self._test_token_authorized_staff_user()

    def test_session_authorized_non_staff_user(self):
        self._test_session_authorized_non_staff_user()

    def test_session_authorized_staff_user(self):
        ItemFactory(is_used=True)
        item_1, item_2 = ItemFactory.create_batch(2, device=self.device, is_used=False)
        response = self.authorized_admin_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [
            {
                'id': item_1.id,
                'identifier': item_1.identifier,
                'cost_type': item_1.cost_type,
            },
            {
                'id': item_2.id,
                'identifier': item_2.identifier,
                'cost_type': item_2.cost_type,
            },
        ])
