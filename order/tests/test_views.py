from django.test import override_settings
from django.urls import reverse
from factory.django import ImageField
from faker import Faker
from rest_framework import status

from api.tests.base import APIViewTestCase
from device.factories import ProductFactory, SpecialtyFactory, CategoryFactory, ManufacturerFactory
from hospital.factories import ClientFactory, AccountFactory, RoleFactory
from hospital.constants import RolePriority
from order.factories import PreferenceFactory, OrderFactory, QuestionFactory
from order.models import Order


class OrderListTestViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.hospital = ClientFactory()
        self.path = reverse('api:hospital:order:orders', args=(self.hospital.id,))

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/clients/{self.hospital.id}/orders')

    def test_unauthorized_post_request(self):
        response = self.client.post(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {
            "detail": "Authentication credentials were not provided."
        })

    def test_non_physician_post_request(self):
        response = self.authorized_client.post(self.path)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'detail': 'Not found.'})

        AccountFactory(user=self.user, client=self.hospital, role=RoleFactory(priority=RolePriority.ADMIN.value))
        response = self.authorized_client.post(self.path)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'detail': 'Not found.'})

    def test_physician_post_request_invalid_data(self):
        AccountFactory(user=self.user, client=self.hospital, role=RoleFactory(priority=RolePriority.PHYSICIAN.value))
        response = self.authorized_client.post(self.path)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {
            'product': ['This field is required.'],
            'procedure_datetime': ['This field is required.'],
            'preference_questions': ['This field is required.']
        })
        data = {
            'product': 1,
            'procedure_datetime': '10:20:30 21-12-2020',
            'cost_type': 3,
            'discounts': [
                {'name': 'CCO', 'value': 10, 'order': 1},
                {'name': 'Repless', 'value': 20, 'order': 2},
            ],
            'preference_questions': [10]
        }
        response = self.authorized_client.post(self.path, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {
            'product': ['Invalid pk "1" - object does not exist.'],
            'procedure_datetime': ['Datetime has wrong format. Use one of these formats instead: '
                                   'YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].'],
            'cost_type': ['"3" is not a valid choice.'],
            'preference_questions': ['Invalid pk "10" - object does not exist.']
        })

    def test_physician_post_request_valid_data(self):
        account = AccountFactory(user=self.user,
                                 client=self.hospital,
                                 role=RoleFactory(priority=RolePriority.PHYSICIAN.value))
        product = ProductFactory()
        questions = PreferenceFactory(questions=QuestionFactory.create_batch(3)).questions.all()
        data = {
            'product': product.id,
            'procedure_datetime': '2020-12-21 10:15:20',
            'cost_type': 2,
            'discounts': [
                {'name': 'CCO', 'value': 10, 'order': 1},
                {'name': 'Repless', 'value': 20, 'order': 2},
            ],
            'preference_questions': [questions[1].id, questions[0].id]
        }
        self.assertEqual(Order.objects.count(), 0)

        response = self.authorized_client.post(self.path, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertCountEqual(response.data.pop('preference_questions'), [questions[0].id, questions[1].id])
        self.assertDictEqual(response.data, {
            'product': product.id,
            'procedure_datetime': '2020-12-21T10:15:20Z',
            'cost_type': 2,
            'discounts': [{'name': 'CCO', 'value': 10, 'order': 1}, {'name': 'Repless', 'value': 20, 'order': 2}],
            'physician': account.id,
            'status': 'New'
        })


class ProductPreferenceListViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.client_1 = ClientFactory()
        self.product = ProductFactory()
        self.question_1, self.question_2 = PreferenceFactory(client=self.client_1, content_object=self.product.category,
                                                             questions=QuestionFactory.create_batch(2)).questions.all()
        self.path = reverse('api:hospital:order:preferences', args=(self.client_1.id, self.product.id))

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/clients/{self.client_1.id}/preferences/products/{self.product.id}')

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_authorized_get_request_returns_list_of_physician_preferences_of_product(self):
        response = self.authorized_client.get(self.path)
        self.assertCountEqual(response.data, [
            {'id': self.question_1.id, 'question': self.question_1.name},
            {'id': self.question_2.id, 'question': self.question_2.name},
        ])


class OrderSummaryListAPIViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        specialty = SpecialtyFactory()
        self.account = AccountFactory.create(role=RoleFactory(priority=RolePriority.PHYSICIAN.value),
                                             user=self.user, specialties=(specialty,))
        self.account_foo = AccountFactory.create(user=self.account.user, specialties=(specialty,))

        self.category_1 = CategoryFactory(specialty=specialty)
        self.category_2 = CategoryFactory(specialty=specialty)

        faker = Faker()
        self.category_1_orders = faker.random_int(min=1, max=20)
        self.category_2_orders = faker.random_int(min=1, max=20)
        self.other_orders = faker.random_int(min=1, max=20)
        self.total_num_orders = self.category_1_orders + self.category_2_orders + self.other_orders
        OrderFactory.create_batch(self.category_1_orders,
                                  physician=self.account,
                                  product=ProductFactory(category=self.category_1))
        OrderFactory.create_batch(self.category_2_orders,
                                  physician=self.account,
                                  product=ProductFactory(category=self.category_2))
        OrderFactory.create_batch(self.other_orders,
                                  physician=AccountFactory(client=self.account.client),
                                  product=ProductFactory(category=self.category_2))
        OrderFactory.create_batch(3, physician=self.account_foo, product=ProductFactory(category=self.category_1))

        self.path = reverse('api:hospital:order:ordersummary', args=(self.account.client.id,))

    def test_api_path(self):
        self.assertEqual(self.path, f'/api/clients/{self.account.client.id}/ordersummary')

    def test_post_method_not_allowed(self):
        response = self.authorized_client.post(self.path)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_view_order_of_other_client(self):
        super().setUp(self.account.user)
        response = self.authorized_client.get(reverse('api:hospital:order:ordersummary',
                                                      args=(ClientFactory().id,)))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {'detail': 'Unauthorized physician access'})

    def test_physician_view_their_own_orders(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data['client'], {
            'id': self.account.client.id,
            'count': self.total_num_orders,
            'name': self.account.client.name,
        })
        self.assertDictEqual(response.data['physician'], {
            'id': self.account.user.id,
            'name': self.account.user.name,
            'count': self.category_1_orders + self.category_2_orders,
        })
        self.assertCountEqual(response.data['categories'], [
            {'id': self.category_1.id, 'name': self.category_1.name, 'count': self.category_1_orders},
            {'id': self.category_2.id, 'name': self.category_2.name, 'count': self.category_2_orders}
        ])

    def test_physician_without_any_order(self):
        client = AccountFactory(role=RoleFactory(priority=RolePriority.PHYSICIAN.value),
                                user=self.user).client
        path = reverse('api:hospital:order:ordersummary', args=(client.id,))

        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data['physician'], {
            'id': self.user.id,
            'count': 0,
            'name': self.user.name
        })


@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class OrderSummaryByCategoryListAPIViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        specialty = SpecialtyFactory()
        self.account = AccountFactory.create(role=RoleFactory(priority=RolePriority.PHYSICIAN.value),
                                             user=self.user, specialties=(specialty,))

        self.category_1 = CategoryFactory(specialty=specialty)
        self.category_2 = CategoryFactory(specialty=specialty)
        self.manufacturer_1 = ManufacturerFactory(image=ImageField(filename='Abbott.jpg'))
        self.manufacturer_2 = ManufacturerFactory(image=ImageField(filename='Simon.jpg'))
        self.product_1 = ProductFactory(category=self.category_1, manufacturer=self.manufacturer_1)
        self.product_2 = ProductFactory(category=self.category_2, manufacturer=self.manufacturer_2)
        self.product_3 = ProductFactory(category=self.category_1, manufacturer=self.manufacturer_2)

        faker = Faker()
        self.product_1_orders = faker.random_int(min=1, max=5)
        self.category_2_orders = faker.random_int(min=1, max=4)
        self.other_orders = faker.random_int(min=1, max=3)
        self.total_num_orders = self.product_1_orders + self.category_2_orders + self.other_orders
        OrderFactory.create_batch(self.product_1_orders,
                                  physician=self.account,
                                  product=self.product_1)
        OrderFactory.create_batch(self.category_2_orders,
                                  physician=self.account,
                                  product=self.product_2)
        OrderFactory.create_batch(self.other_orders,
                                  physician=AccountFactory(client=self.account.client),
                                  product=self.product_3)
        self.path = reverse('api:hospital:order:ordersummary_by_category',
                            args=(self.account.client.id, self.category_1.id))

    def test_api_path(self):
        self.assertEqual(
            self.path, f'/api/clients/{self.account.client.id}/ordersummary/categories/{self.category_1.id}')

    def test_post_method_not_allowed(self):
        response = self.authorized_client.post(self.path)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_view_order_of_other_client(self):
        client = ClientFactory()
        path = reverse('api:hospital:order:ordersummary_by_category', args=(client.id, self.category_1.id))

        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {'detail': 'Unauthorized physician access'})

        AccountFactory(client=client, user=self.user, role=RoleFactory(priority=RolePriority.ADMIN.value))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {'detail': 'Unauthorized physician access'})

    def test_physician_view_their_own_order(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [{
            'id': self.product_1.id, 'name': self.product_1.name, 'count': self.product_1_orders,
            'manufacturer': {
                'id': self.manufacturer_1.id,
                'name': self.manufacturer_1.name,
                'short_name': self.manufacturer_1.short_name,
                'image': self.manufacturer_1.image.url
            }
        }])

    def test_physician_without_any_order(self):
        client = self.account.client
        category = CategoryFactory()
        OrderFactory(physician=AccountFactory(client=client),
                     product=ProductFactory(category=category))
        path = reverse('api:hospital:order:ordersummary_by_category', args=(client.id, category.id))

        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


class PreferenceByOrderedProductListViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.account = AccountFactory(user=self.user, role=RoleFactory(priority=RolePriority.PHYSICIAN.value))
        self.product = ProductFactory()
        preference = PreferenceFactory(client=self.account.client, questions=QuestionFactory.create_batch(3))
        self.question_1, self.question_2, self.question_3 = preference.questions.all()
        OrderFactory.create_batch(2,
                                  physician=self.account,
                                  product=self.product,
                                  preference_questions=(self.question_1, self.question_2))
        OrderFactory.create_batch(3,
                                  physician=self.account,
                                  product=self.product,
                                  preference_questions=(self.question_2, self.question_3))
        self.path = reverse('api:hospital:order:order_preferences', args=(self.account.client.id, self.product.id))

    def test_api_path(self):
        self.assertEqual(self.path,
                         f'/api/clients/{self.account.client.id}/orders/products/{self.product.id}/preferences')

    def test_post_method_not_allowed(self):
        response = self.authorized_client.post(self.path)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_view_order_preferences(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [
            {'id': self.question_1.id, 'question': self.question_1.name, 'count': 2},
            {'id': self.question_2.id, 'question': self.question_2.name, 'count': 5},
            {'id': self.question_3.id, 'question': self.question_3.name, 'count': 3},
        ])

    def test_view_order_preferences_without_any_order(self):
        other_product = ProductFactory()
        path = reverse('api:hospital:order:order_preferences', args=(self.account.client.id, other_product.id))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, [])

    def test_view_order_preferences_of_other_client(self):
        path = reverse('api:hospital:order:order_preferences', args=(ClientFactory().id, self.product.id))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_id_not_exist(self):
        path = reverse('api:hospital:order:order_preferences', args=(self.account.client.id, 101))
        response = self.authorized_client.get(path)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
