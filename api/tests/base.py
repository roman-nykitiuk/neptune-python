from knox.models import AuthToken
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from account.factories import UserFactory


class APIViewTestCase(APITestCase):
    def setUp(self, user=None):
        super().setUp()
        self.user = user if user is not None else UserFactory()
        self.token = AuthToken.objects.create(self.user)
        self.authorized_client = self.get_authorized_client()

    def _test_get_method_unauthorized_user(self, path=None):
        response = self.client.get(path if path else self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertDictEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertDictEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

        self.client.credentials(HTTP_AUTHORIZATION='Token invalid_token')
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertDictEqual(response.data, {
            'detail': 'Invalid token.'
        })

    def get_authorized_client(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        return client

    def get_session_authorized_client(self, user=None):
        user = user or self.user
        client = APIClient()
        client.login(username=user.email, password='password1')
        return client


class StaffAPIViewTestCase(APIViewTestCase):
    def setUp(self, user=None):
        super().setUp(user)
        self.authorized_admin_client = self.get_session_authorized_client(user=UserFactory(is_staff=True))

    def _test_token_authorized_staff_user(self):
        self.user.is_staff = True
        self.user.save()
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    def _test_session_authorized_non_staff_user(self):
        response = self.get_session_authorized_client().get(self.path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.data, {
            'detail': 'You do not have permission to perform this action.'
        })
