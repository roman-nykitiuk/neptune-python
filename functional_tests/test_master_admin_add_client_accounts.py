from functional_tests.base import MasterAdminTestCase
from hospital.factories import RoleFactory, ClientFactory, AccountFactory


class ClientAccountsListingAdminTestCase(MasterAdminTestCase):
    def setUp(self):
        doctor = RoleFactory(name='Physician', priority=1)
        hospital_admin = RoleFactory(name='Hospital Administrator', priority=10)
        self.client_1, self.client_2 = ClientFactory.create_batch(2)
        self.account_1 = AccountFactory(client=self.client_1, role=doctor)
        self.account_2 = AccountFactory(client=self.client_1, role=hospital_admin)
        self.account_3, self.account_4 = AccountFactory.create_batch(2, client=self.client_2, role=doctor)

        super(ClientAccountsListingAdminTestCase, self).setUp()
        self.log_in_master_admin()
        self.visit_reverse('admin:hospital_account_changelist')
        self.wait_for_element_contains_text('#content h1', 'Select user account to change')

    def test_accounts_list_order_by_client_and_descending_role_priority(self):
        self.wait_for_element_contains_text('.paginator', '4 user accounts')
        rows = self.find_elements('#result_list tbody tr')
        displayed_accounts = (
            (self.client_1, 'Hospital Administrator', self.account_2),
            (self.client_1, 'Physician', self.account_1),
            (self.client_2, 'Physician', self.account_3),
            (self.client_2, 'Physician', self.account_4),
        )
        for index, row in enumerate(rows):
            client, role, account = displayed_accounts[index]
            self.assertTrue(client.name in self.find_element('.field-client_link', parent=row).text)
            self.assertTrue(role in self.find_element('.field-role', parent=row).text)
            self.assertTrue(account.user.email in self.find_element('.field-user', parent=row).text)

    def test_link_to_client(self):
        self.find_link(self.client_1.name, self.find_elements('#result_list tbody tr')[0]).click()
        self.wait_for_element_contains_text('#content h1', 'Change client')
        self.assert_element_attribute_value('input#id_name', self.client_1.name)
