from functional_tests.base import MasterAdminTestCase


class MasterAdminLoginTestCase(MasterAdminTestCase):
    def setUp(self):
        super(MasterAdminLoginTestCase, self).setUp()
        self.visit('master')
        self.wait_for_element_contains_text('#site-name', 'NeptunePPA administration')

    def test_login_with_email_success(self):
        self.fill_form_field_with_text('username', self.master_admin.email)
        self.fill_form_field_with_text('password', 'neptune123')
        self.click_submit_button()
        self.wait_for_element_contains_text('#content h1', 'Site administration')

    def test_login_with_email_error(self):
        self.fill_form_field_with_text('username', self.master_admin.email)
        self.fill_form_field_with_text('password', 'wrongpassword')
        self.click_submit_button()
        self.wait_for_element_contains_text('.errornote', 'Please enter the correct email address and password')
