from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from hospital.models import Client, Role, Account

User = get_user_model()


class ImportClientsCommandTestCase(TestCase):
    def run_command_and_assert(self):
        call_command('import_clients', '--file_path=hospital/tests/clients-data.xls')
        self.assertEqual(Client.objects.count(), 3)
        self.assertEqual(Role.objects.count(), 2)

        self.assertCountEqual(User.objects.all().values_list('email', 'name'), (
            ('Ethan@gmail.com', 'Ethan'),
            ('charles@gmail.com', 'charles'),
        ))
        self.assertCountEqual(Account.objects.all().values_list('user__email', 'client__name', 'role__name'), (
            ('Ethan@gmail.com',	'Nw hosp1',	'Physician'),
            ('charles@gmail.com', 'UVMC',	'Administrator'),
            ('charles@gmail.com', 'Keene State General', 'Administrator'),
        ))

    def test_command_multiple_runs(self):
        self.run_command_and_assert()
        self.run_command_and_assert()

    def test_raise_system_exit_if_file_not_found(self):
        with self.assertRaises(SystemExit) as ex:
            call_command('import_clients', '--file_path=file-not-found.xls')
            self.assertEqual(ex.exception.code, 1)
