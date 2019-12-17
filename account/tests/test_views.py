from django.urls import reverse
from rest_framework import status

from api.tests.base import APIViewTestCase
from hospital.factories import ClientFactory, AccountFactory


class UserViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.path = reverse('api:account:user')

    def test_api_path(self):
        self.assertEqual(self.path, '/api/account/user')

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_get_method_with_authenticated_user(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {
            'email': self.user.email,
            'name': self.user.name,
            'default_client': None,
            'admin_client': None,
        })

    def test_put_method_authenticated_user_invalid_params(self):
        response = self.authorized_client.put(self.path)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {
            'default_client_id': ['This field is required.']
        })

        response = self.authorized_client.put(self.path, {'default_client_id': 1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {
            'default_client_id': ['Invalid client.']
        })

        client = ClientFactory()
        response = self.authorized_client.put(self.path, {'default_client_id': client.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {
            'default_client_id': ['Invalid client.']
        })

    def test_put_method_authenticated_user_valid_params(self):
        account1, account2 = AccountFactory.create_batch(2, user=self.user)
        client1 = account1.client
        client2 = account2.client

        response = self.authorized_client.put(self.path, {'default_client_id': client1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {
            'email': self.user.email,
            'name': self.user.name,
            'default_client': {
                'id': client1.id,
                'name': client1.name,
                'image': None
            },
            'admin_client': None,
        })

        response = self.authorized_client.put(self.path, {'default_client_id': client2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {
            'email': self.user.email,
            'name': self.user.name,
            'default_client': {
                'id': client2.id,
                'name': client2.name,
                'image': None
            },
            'admin_client': None,
        })

    def test_post_method_not_allowed(self):
        response = self.authorized_client.post(self.path)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
