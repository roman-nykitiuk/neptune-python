from django.urls import reverse
from rest_framework import status

from api.tests.base import APIViewTestCase
from hospital.factories import ClientFactory, AccountFactory


class ClientListViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.path = reverse('api:hospital:clients')
        self.client_1, self.client_2 = ClientFactory.create_batch(2)
        AccountFactory(user=self.user, client=self.client_1)
        AccountFactory(user=self.user, client=self.client_2)
        AccountFactory(client=self.client_2)
        AccountFactory.create_batch(2)

    def test_api_path(self):
        self.assertEqual(self.path, '/api/clients')

    def test_post_method_not_allowed(self):
        response = self.authorized_client.post(self.path)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_method_unauthorized_user(self):
        self._test_get_method_unauthorized_user()

    def test_get_method_authenticated_user_return_user_clients(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertCountEqual(response.data, [
            {'id': self.client_1.id, 'name': self.client_1.name, 'image': None},
            {'id': self.client_2.id, 'name': self.client_2.name, 'image': None},
        ])
