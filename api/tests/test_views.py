from django.urls import reverse
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from rest_framework import status
from rest_framework.test import APITestCase

from account.factories import UserFactory
from api.tests.base import APIViewTestCase
from hospital.constants import RolePriority
from hospital.factories import AccountFactory, RoleFactory


class LoginAPIViewTestCase(APITestCase):
    def setUp(self):
        self.path = reverse('api:login')
        self.user = UserFactory(email='admin@neptune.com', name='Dr. Admin')

    def test_api_path(self):
        self.assertEqual(self.path, '/api/login')

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

        admin_client = AccountFactory(user=self.user, role=RoleFactory(priority=RolePriority.ADMIN.value)).client
        response = self.client.post(self.path, {'email': 'admin@neptune.com', 'password': 'password1'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': 'Unauthorized physician access'})

        AccountFactory(user=self.user, role=RoleFactory(priority=RolePriority.PHYSICIAN.value))
        for token_count in range(1, 3):
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


class LogoutAPIViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.path = reverse('api:logout')

    def test_api_path(self):
        self.assertEqual(self.path, '/api/logout')

    def test_get_method_not_allowed(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_method_unauthorized(self):
        response = self.client.post(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertDictEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    def test_post_method_authorized_removes_current_token_only(self):
        token = AuthToken.objects.create(self.user)
        AuthToken.objects.create(UserFactory())
        self.assertEqual(AuthToken.objects.count(), 3)
        self.assertEqual(self.user.auth_token_set.count(), 2)

        response = self.authorized_client.post(self.path)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user.auth_token_set.count(), 1)
        self.assertEqual(AuthToken.objects.count(), 2)

        response = self.authorized_client.post(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.post(self.path)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user.auth_token_set.count(), 0)
        self.assertEqual(AuthToken.objects.count(), 1)


class LogoutAllAPIViewTestCase(APIViewTestCase):
    def setUp(self):
        super().setUp()
        self.path = reverse('api:logout_all')

    def test_api_path(self):
        self.assertEqual(self.path, '/api/logout/all')

    def test_get_method_not_allowed(self):
        response = self.authorized_client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_method_unauthorized(self):
        response = self.client.post(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertDictEqual(response.data, {
            'detail': 'Authentication credentials were not provided.'
        })

    def test_post_method_authorized_removes_current_token_only(self):
        token = AuthToken.objects.create(self.user)
        AuthToken.objects.create(UserFactory())
        self.assertEqual(AuthToken.objects.count(), 3)
        self.assertEqual(self.user.auth_token_set.count(), 2)

        response = self.authorized_client.post(self.path)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user.auth_token_set.count(), 0)
        self.assertEqual(AuthToken.objects.count(), 1)

        response = self.authorized_client.post(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.post(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
