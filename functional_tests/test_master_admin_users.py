from functional_tests.base import MasterAdminTestCase
from hospital.factories import RoleFactory, ClientFactory, AccountFactory


class UsersListingAdminTestCase(MasterAdminTestCase):
    def setUp(self):
        doctor = RoleFactory(name='Physician', priority=1)
        hospital_admin = RoleFactory(name='Hospital Administrator', priority=10)
        self.client_1, self.client_2 = ClientFactory.create_batch(2)
        self.user_1 = AccountFactory(client=self.client_1, role=doctor).user
        self.user_2 = AccountFactory(client=self.client_1, role=hospital_admin).user
        AccountFactory(user=self.user_1, client=self.client_2, role=hospital_admin)

        super(UsersListingAdminTestCase, self).setUp()
        self.log_in_master_admin()
        self.visit_reverse('admin:account_user_changelist')
        self.wait_for_element_contains_text('.model-user.change-list #content h1', 'Select user to change')

    def assert_user_clients(self, displayed_user_accounts):

        rows = self.find_elements('#result_list tbody tr')
        for row in rows:
            user_email = self.find_element('.field-email', parent=row).text
            user_accounts_text = self.find_element('.field-accounts', parent=row).text
            for account in displayed_user_accounts[user_email]:
                self.assertTrue(account in user_accounts_text)

    def test_users_list_show_associated_clients(self):
        self.wait_for_element_contains_text('.paginator', f'3 users')

        displayed_user_accounts = {
            self.user_1.email: [f'Physician at {self.client_1.name}',
                                f'Hospital Administrator at {self.client_2.name}'],
            self.user_2.email: [f'Hospital Administrator at {self.client_1.name}'],
            self.master_admin.email: [],
        }
        self.assert_user_clients(displayed_user_accounts)

    def test_link_to_client(self):
        result_div = self.find_element('.results')
        self.find_link(self.client_2.name, parent=result_div).click()
        self.wait_for_element_contains_text('.model-client.change-form #content h1', 'Change client')
        self.assert_element_attribute_value('input#id_name', self.client_2.name)

    def test_filter_users_by_role(self):
        self.assert_elements_count(('#changelist-filter ul:first-of-type li'), 3)
        self.find_link('Physician').click()
        self.wait_for_element_contains_text('#changelist-search .small', '1 result (3 total)')
        displayed_user_accounts = {
            self.user_1.email: [f'Physician at {self.client_1.name}',
                                f'Hospital Administrator at {self.client_2.name}'],
        }
        self.assert_user_clients(displayed_user_accounts)

        self.find_link('Hospital Administrator').click()
        self.wait_for_element_contains_text('#changelist-search .small', '2 results (3 total)')
        displayed_user_accounts = {
            self.user_1.email: [f'Physician at {self.client_1.name}',
                                f'Hospital Administrator at {self.client_2.name}'],
            self.user_2.email: [f'Hospital Administrator at {self.client_1.name}'],
        }
        self.assert_user_clients(displayed_user_accounts)

    def test_filter_users_by_client(self):
        self.assert_elements_count(('#changelist-filter ul:nth-of-type(2) li'), 3)
        self.find_link(self.client_2.name).click()
        self.wait_for_element_contains_text('#changelist-search .small', '1 result (3 total)')
        displayed_user_accounts = {
            self.user_1.email: [f'Physician at {self.client_1.name}',
                                f'Hospital Administrator at {self.client_2.name}'],
        }
        self.assert_user_clients(displayed_user_accounts)

        self.find_link(self.client_1.name).click()
        self.wait_for_element_contains_text('#changelist-search .small', '2 results (3 total)')
        displayed_user_accounts = {
            self.user_1.email: [f'Physician at {self.client_1.name}'],
            self.user_2.email: [f'Hospital Administrator at {self.client_1.name}']
        }
        self.assert_user_clients(displayed_user_accounts)
