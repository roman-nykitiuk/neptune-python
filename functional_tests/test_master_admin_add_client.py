import os
from unittest.mock import MagicMock, patch

from django.conf import settings
from factory.django import ImageField

from account.factories import UserFactory
from device.factories import SpecialtyFactory, CategoryFactory, ProductFactory
from functional_tests.base import MasterAdminTestCase
from hospital.factories import ClientFactory, DeviceFactory, RoleFactory
from neptune.storages import S3Boto3Storage
from price.factories import ClientPriceFactory


class ClientAdminTestCase(MasterAdminTestCase):
    def setUp(self):
        super(ClientAdminTestCase, self).setUp()
        self.log_in_master_admin()
        self.visit_reverse('admin:hospital_client_add')
        self.wait_for_element_contains_text('#content h1', 'Add client')

    def test_add_new_client_default_view(self):
        self.assert_element_attribute_value('#id_name', '')
        self.assert_element_attribute_value('#id_street', '')
        self.assert_element_attribute_value('#id_city', '')
        self.assert_element_attribute_value('#id_state', '')
        self.assert_option_is_selected('#id_country', 'United States of America')

    def test_add_client_failure(self):
        self.click_submit_button()
        self.wait_for_element_contains_text('.errornote', 'Please correct the errors below.')
        self.wait_for_element_contains_text('.field-name .errorlist', 'This field is required.')
        self.wait_for_element_contains_text('.field-street .errorlist', 'This field is required.')
        self.wait_for_element_contains_text('.field-state .errorlist', 'This field is required.')
        self.wait_for_element_contains_text('.field-city .errorlist', 'This field is required.')

    def test_add_client_success(self):
        self.fill_form_field_with_text('name', 'Central Hospital')
        self.fill_form_field_with_text('street', 'Light Revenue')
        self.fill_form_field_with_text('city', 'New York')
        self.fill_form_field_with_text('state', 'Washington DC')
        self.select_option('#id_country', 'Canada')

        self.click_save_and_continue()
        self.wait_for_element_contains_text(
            '.success',
            'The client "Central Hospital" was added successfully. You may edit it again below.'
        )
        self.assert_element_attribute_value('#id_name', 'Central Hospital')
        self.assert_element_attribute_value('#id_street', 'Light Revenue')
        self.assert_element_attribute_value('#id_city', 'New York')
        self.assert_element_attribute_value('#id_state', 'Washington DC')
        self.assert_option_is_selected('#id_country', 'Canada')


class ClientAdminImageTestCase(MasterAdminTestCase):
    def setUp(self):
        super(ClientAdminImageTestCase, self).setUp()
        self.log_in_master_admin()

        self.storage_mock = MagicMock(spec=S3Boto3Storage, name='StorageMock')
        self.storage_mock.url = MagicMock(name='url')
        with open(str(os.path.join(settings.FIXTURE_DIR, 'client_image_base64'))) as file:
            self.image_data = file.read().strip()
        self.storage_mock.url.return_value = self.image_data
        self.storage_mock.save.return_value = 'test_image.jpg'

    def test_show_client_image(self):
        with patch('django.core.files.storage.default_storage._wrapped', self.storage_mock):
            client = ClientFactory(name='Central Hospital', image=ImageField())
            self.visit_reverse('admin:hospital_client_change', client.id)
            self.wait_for_element_contains_text('#content h1', 'Change client')
            self.assert_element_attribute_value('.file-upload img', self.image_data, attr='src')
            self.wait_for_element_contains_text('.file-upload', 'Currently: test_image.jpg')

            self.find_element('#image-clear_id').click()
            self.click_save_and_continue()
            self.wait_for_element_contains_text(
                '.messagelist .success',
                'The client "Central Hospital" was changed successfully. You may edit it again below.'
            )
            self.assert_element_to_disappear('.file-upload')

    def test_upload_client_image(self):
        with patch('django.core.files.storage.default_storage._wrapped', self.storage_mock):
            client = ClientFactory(name='Central Hospital', image=None)
            upload_file_path = os.path.join(settings.FIXTURE_DIR, 'client_image.png')

            self.visit_reverse('admin:hospital_client_change', client.id)
            self.wait_for_element_contains_text('#content h1', 'Change client')
            self.assert_element_to_disappear('.file-upload')

            self.fill_form_field_with_text('image', upload_file_path)
            self.click_save_and_continue()
            self.wait_for_element_contains_text('.file-upload', 'Currently: test_image.jpg')
            self.assert_element_attribute_value('.file-upload img', self.image_data, attr='src')


class ClientSpecialtiesAdminTestCase(MasterAdminTestCase):
    def setUp(self):
        super().setUp()
        self.log_in_master_admin()
        self.specialty = SpecialtyFactory(name='Cardiac Rhythm Management')
        self.client = ClientFactory()
        category = CategoryFactory(specialty=self.specialty)
        product = ProductFactory(category=category)
        DeviceFactory(client=self.client)
        ClientPriceFactory(client=self.client, product=product)

    def test_show_specialties_that_have_product_price_set(self):
        self.visit_reverse('admin:hospital_client_change', self.client.id)
        self.wait_for_element_contains_text('#client_form .field-specialties', 'Cardiac Rhythm Management')
        self.assert_elements_count('.field-specialties ul li', count=1)


class ChildrenClientAdminTestCase(MasterAdminTestCase):
    def setUp(self):
        super(ChildrenClientAdminTestCase, self).setUp()
        self.log_in_master_admin()
        self.client, self.client2, self.client3 = ClientFactory.create_batch(3)

    def test_add_children_clients(self):
        self.visit_reverse('admin:hospital_client_change', self.client.id)
        self.wait_for_element_contains_text('#content h1', 'Change client')

        self.browser.execute_script("$('#id_children').select2('open');")
        self.assert_elements_count('#select2-id_children-results .select2-results__option', 2)
        options = self.find_element('#select2-id_children-results').text
        self.assertTrue(self.client2.name in options)
        self.assertTrue(self.client3.name in options)

        self.select_option('#id_children', self.client3.name)
        self.click_save_and_continue()
        self.wait_for_success_message(f'The client "{self.client.name}" was changed successfully.')

        self.assert_elements_count('.field-children .select2-selection__choice', 1)
        self.wait_for_element_contains_text('.field-children .select2-selection__rendered', self.client3.name)

        self.visit_reverse('admin:hospital_client_changelist')
        self.wait_for_element_contains_text('.model-client.change-list', 'Select client to change')
        self.assert_elements_count('#result_list tbody tr', 3)

        rows = self.find_elements('#result_list tbody tr')
        for row in rows:
            if self.client3.name in row.text:
                self.assertEqual(row.find_element_by_css_selector('.field-parent_client').text, self.client.name)

    def test_remove_children_clients(self):
        self.client.set_children(children_ids=[self.client2.id])
        self.visit_reverse('admin:hospital_client_change', self.client.id)
        self.wait_for_element_contains_text('#content h1', 'Change client')

        self.assert_elements_count('.select2-selection__rendered .select2-selection__choice', 1)
        self.wait_for_element_contains_text('.select2-selection__rendered .select2-selection__choice',
                                            self.client2.name)

        self.find_element('.select2-selection__choice__remove').click()
        self.click_save_and_continue()
        self.wait_for_success_message(f'The client "{self.client.name}" was changed successfully.')
        self.assert_elements_count('.select2-selection__rendered .select2-selection__choice', 0)

    def test_create_client_with_the_new_button(self):
        self.visit_reverse('admin:hospital_client_change', self.client.id)
        self.find_element('#add_id_children').click()
        self.browser.switch_to_window(self.browser.window_handles[1])
        self.wait_for(lambda: self.assertEqual(self.browser.title, 'Add client | NeptunePPA Admin'))
        self.wait_for_element_contains_text('#content h1', 'Add client')
        self.fill_form_field_with_text('name', 'Indo hospital')
        self.fill_form_field_with_text('street', 'Street1')
        self.fill_form_field_with_text('city', 'Jakarta')
        self.fill_form_field_with_text('state', 'Jakarta')
        self.click_submit_button()
        self.wait_for(lambda: self.assertEqual(len(self.browser.window_handles), 1))
        self.browser.switch_to_window(self.browser.window_handles[0])
        children = self.find_elements('.field-children .select2-selection__choice')
        self.assertEqual(len(children), 1)
        self.assertTrue('Indo hospital' in children[0].text)


class ClientsListingAdminTestCase(MasterAdminTestCase):
    def setUp(self):
        super(ClientsListingAdminTestCase, self).setUp()
        self.client1 = ClientFactory(name='NS Global', city='city1', state='state1')
        self.client2 = ClientFactory(name='NS Vietnam', city='city2', state='state2')
        self.client3 = ClientFactory(name='International hospital', city='city3', state='state3')
        self.log_in_master_admin()

    def _visit_clients_changelist(self):
        self.visit_reverse('admin:hospital_client_changelist')
        self.wait_for_element_contains_text('.model-client.change-list #content h1', 'Select client to change')

    def test_search_client_by_name(self):
        self._visit_clients_changelist()
        self.wait_for_element_contains_text('.paginator', '3 clients')

        self.browser.execute_script('$("#searchbar").val("NS")')
        self.click_submit_button()
        self.wait_for_element_contains_text('#changelist-search .small', '2 results (3 total)')
        self.assert_elements_count('#result_list tbody tr', 2)

        found_clients = self.find_element('#result_list').text
        self.assertTrue('NS Global' in found_clients)
        self.assertTrue('NS Vietnam' in found_clients)


class FilterClientsByDevicesAdminTestCase(MasterAdminTestCase):
    def _create_product_for_client(self, product, category, specialty, client):
        DeviceFactory(
            client=client,
            product=ProductFactory(
                name=product,
                category=CategoryFactory(name=category, specialty=specialty)
            ))

    def setUp(self):
        super(FilterClientsByDevicesAdminTestCase, self).setUp()
        self.client1 = ClientFactory(name='NS Global')
        self.client2 = ClientFactory(name='NS Vietnam')
        self.client3 = ClientFactory(name='International hospital')

        specialty = SpecialtyFactory(name='Structural Heart')
        specialty2 = SpecialtyFactory(name='Interventional Cardiology')
        SpecialtyFactory(name='Neuromodulation')

        self._create_product_for_client(product='LINQ', category='TAVR Delivery System',
                                        specialty=specialty, client=self.client3)
        self._create_product_for_client(product='Pacemaker', category='TAVR Implant System',
                                        specialty=specialty, client=self.client2)
        self._create_product_for_client(product='Assurity', category='​Drug Eluting Stents',
                                        specialty=specialty2, client=self.client1)

        self.log_in_master_admin()
        self.visit_reverse('admin:hospital_client_changelist')
        self.wait_for_element_contains_text('.model-client.change-list #content h1', 'Select client to change')

    def test_search_by_specialty_name(self):
        self.fill_form_field_with_text('q', 'Structural')
        self.click_submit_button()
        self.wait_for_element_contains_text('#changelist-search .small', '2 results (3 total)')
        self.assert_elements_count('#result_list tbody tr', 2)
        found_clients = self.find_element('#result_list').text
        self.assertTrue(self.client2.name in found_clients)
        self.assertTrue(self.client3.name in found_clients)

    def test_search_by_category_name(self):
        self.fill_form_field_with_text('q', 'Implant')
        self.click_submit_button()
        self.wait_for_element_contains_text('#changelist-search .small', '1 result (3 total)')
        self.assert_elements_count('#result_list tbody tr', 1)
        self.wait_for_element_contains_text('#result_list tbody .field-name', self.client2.name)

    def test_search_by_product_name(self):
        self.fill_form_field_with_text('q', 'Assurity')
        self.click_submit_button()
        self.wait_for_element_contains_text('#changelist-search .small', '1 result (3 total)')
        self.assert_elements_count('#result_list tbody tr', 1)
        self.wait_for_element_contains_text('#result_list tbody .field-name', self.client1.name)

    def test_filter_panel(self):
        self.wait_for_element_contains_text('#changelist-filter', 'By Specialty')

        filtered_options = self.find_element('#changelist-filter')
        filtered_options_text = filtered_options.text
        self.assertEqual(len(filtered_options.find_elements_by_css_selector('ul li')), 4)
        self.wait_for_element_contains_text('#changelist-filter li.selected', 'All')
        self.assertTrue('Structural Heart' in filtered_options_text)
        self.assertTrue('Interventional Cardiology' in filtered_options_text)
        self.assertTrue('Neuromodulation' in filtered_options_text)

        self.find_link('Structural Heart').click()
        self.wait_for_element_contains_text('#changelist-search .small', '2 results (3 total)')

        self.find_link('Interventional Cardiology').click()
        self.wait_for_element_contains_text('#changelist-search .small', '1 result (3 total)')

        self.find_link('Neuromodulation').click()
        self.wait_for_element_contains_text('#changelist-search .small', '0 results (3 total)')


class AccountsInlineAdminTestCase(MasterAdminTestCase):
    def setUp(self):
        super(AccountsInlineAdminTestCase, self).setUp()
        self.log_in_master_admin()
        self.client = ClientFactory(name='NS Global')
        self.client2 = ClientFactory(name='NS Vietnam')
        self.role = RoleFactory(name='Physician')
        self.user1 = UserFactory(email='user1@ea.com')
        self.user2 = UserFactory(email='user2@ea.com')
        self.specialty_1, self.specialty_2 = SpecialtyFactory.create_batch(2)

    def test_add_user_to_client(self):
        self.visit_reverse('admin:hospital_client_change', self.client.id)
        self.wait_for_element_contains_text('#content h1', 'Change client')

        # click Add another Account and select values
        self.wait_for(lambda: self.assertFalse(self.find_element('#account_set-2-group table').is_displayed()))
        self.find_element('#account_set-2-group h2').click()
        self.find_element('#account_set-2-group .add-row a').click()
        self.wait_for(lambda: self.find_element('#account_set-2-0').is_displayed())
        self.select_option('#id_account_set-2-0-user', self.user1.email)
        self.select_option('#id_account_set-2-0-role', self.role.name)
        self.select_option('#id_account_set-2-0-specialties', self.specialty_1.name)
        self.select_option('#id_account_set-2-0-specialties', self.specialty_2.name)
        self.click_save_and_continue()

        # Assert user1 is added into accounts group
        self.wait_for_success_message('The client "NS Global" was changed successfully.')
        self.wait_for_element_contains_text('#account_set-0 .field-user', self.user1.email)
        self.assert_option_is_selected('#id_account_set-0-role', self.role.name)
        self.assert_options_are_selected('#id_account_set-0-specialties',
                                         [self.specialty_1.name, self.specialty_2.name])

        # Assert user1 is still in the select when user adds another account
        self.wait_for(lambda: self.assertFalse(self.find_element('#account_set-2-group table').is_displayed()))
        self.find_element('#account_set-2-group h2').click()
        self.wait_for_element_contains_text('#account_set-2-group .add-row a', 'Add another User account')
        self.find_element('#account_set-2-group .add-row a').click()
        self.wait_for(lambda: self.find_element('#account_set-2-0').is_displayed())
        select_text = self.find_element('#id_account_set-2-0-user').text
        self.assertTrue(self.user1.email in select_text)
        self.assertTrue(self.user2.email in select_text)
