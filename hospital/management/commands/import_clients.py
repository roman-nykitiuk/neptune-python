from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from hospital.models import Client, Role, Account
from neptune.management.commands.import_data import ImportCommand

User = get_user_model()


class Command(ImportCommand):
    help = 'Import clients, hospital admins and doctors'

    def import_data(self):
        imported_clients = {}
        imported_roles = {}
        imported_users = {}
        imported_accounts = {}

        for index, row in self.data.iterrows():
            row = (str(data).strip() for data in row)
            user_name, email, client_names, role_name, specialty, login_counts, orders_count = row
            client_names = client_names.split(',')
            user_id = imported_users.setdefault(
                email,
                User.objects.get_or_create(email=email, name=user_name)[0].id
            )
            role = imported_roles.setdefault(
                role_name,
                Role.objects.get_or_create(name=role_name)[0]
            )
            for client_name in client_names:
                client_id = imported_clients.setdefault(
                    client_name,
                    Client.objects.get_or_create(name=client_name)[0].id
                )

                imported_accounts.setdefault(
                    f'{client_id}-{user_id}-{role.id}',
                    self.get_account(user_id, client_id, role)
                )

                print(f'Import account {email} as {role_name} at hospital {client_name}')

    def get_account(self, user_id, client_id, role):
        try:
            account = Account.objects.get(user_id=user_id, client_id=client_id)
            if account.role.name != role.name:
                print(f'WARNING: User {account.user.email} exists as role {account.role} at hospital {account.client}')
        except ObjectDoesNotExist:
            account = Account.objects.get_or_create(user_id=user_id, client_id=client_id, role=role)[0]

        return account
