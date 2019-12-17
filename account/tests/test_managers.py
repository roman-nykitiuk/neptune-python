from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

User = get_user_model()


class CreateSuperUserManagerTestCase(TestCase):
    def setUp(self):
        self.assertEqual(User.objects.count(), 0)

    def test_create_superuser(self):
        master_admin = User.objects.create_superuser('admin@neptune.com', 'neptune123')

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(master_admin.email, 'admin@neptune.com')
        self.assertTrue(master_admin.check_password('neptune123'))
        self.assertTrue(master_admin.is_superuser)
        self.assertTrue(master_admin.is_staff)

    def test_invalid_assigned_admin_fields(self):
        self.assertRaises(
            ValueError,
            User.objects.create_superuser,
            'admin@neptune.com', 'neptune123', is_staff=False
        )
        self.assertRaises(
            ValueError,
            User.objects.create_superuser,
            'admin@neptune.com', 'neptune123', is_superuser=False
        )

        self.assertEqual(User.objects.count(), 0)


class CreateUserManagerTestCase(TestCase):
    def setUp(self):
        self.assertEqual(User.objects.count(), 0)

    def test_user_created_with_valid_info(self):
        user = User.objects.create_user('doctor@neptune.com', is_staff=True)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.email, 'doctor@neptune.com')
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.check_password(None))

    def test_raise_intergiry_error_when_create_user_with_taken_email(self):
        User.objects.create_user(email='doctor@neptune.com', password='doctor123')
        self.assertRaises(IntegrityError, User.objects.create_user, 'doctor@neptune.com', password='doctor')

    def test_raise_value_error_when_create_user_with_empty_email(self):
        self.assertRaises(ValueError, User.objects.create_user, None)
