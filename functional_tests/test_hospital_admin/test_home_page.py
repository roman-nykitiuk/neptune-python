from .base import HospitalAdminTestCase


class HomePageTestCase(HospitalAdminTestCase):
    def setUp(self):
        super(HomePageTestCase, self).setUp()
        self.visit('admin/login/')

    def test_contains_login_form(self):
        self.wait_for_element_contains_text('#frontend', 'Login')

    def test_login_errors(self):
        self.fill_form_field_with_text('email', 'physician@neptune.com')
        self.fill_form_field_with_text('password', 'invalid-password')
        self.find_element('input[type=submit]').click()
        self.wait_for_element_contains_text('#frontend', 'Invalid email/password.')

        self.fill_form_field_with_text('email', 'physician@neptune.com')
        self.fill_form_field_with_text('password', 'password1')
        self.find_element('input[type=submit]').click()
        self.wait_for_element_contains_text('#frontend', 'Unauthorized admin access')

        self.fill_form_field_with_text('email', 'admin@neptune.com')
        self.fill_form_field_with_text('password', 'invalid-password')
        self.find_element('input[type=submit]').click()
        self.wait_for_element_contains_text('#frontend', 'Invalid email/password.')

    def test_login_success(self):
        self.fill_form_field_with_text('email', 'admin@neptune.com')
        self.fill_form_field_with_text('password', 'password1')
        self.find_element('input[type=submit]').click()
        self.wait_for_element_contains_text('#frontend', self.admin.name.upper())
