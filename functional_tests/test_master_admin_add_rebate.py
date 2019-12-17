from device.factories import ManufacturerFactory, ProductFactory, CategoryFactory, SpecialtyFactory
from functional_tests.base import MasterAdminTestCase
from hospital.factories import ClientFactory


class RebateAdminTestCase(MasterAdminTestCase):
    def setUp(self):
        super().setUp()
        self.log_in_master_admin()
        biotronic = ManufacturerFactory(name='Biotronic')
        medtronik = ManufacturerFactory(name='Medtronik')
        ClientFactory(name='Children Hospital')
        ClientFactory(name='Central hospital')
        category = CategoryFactory(name='Balloons', specialty=SpecialtyFactory(name='Accessories'))
        ProductFactory(name='Entrisa', manufacturer=medtronik,
                       category=CategoryFactory(name='DDD pacemaker', specialty=SpecialtyFactory(name='CRD')))
        ProductFactory(name='Apex', manufacturer=medtronik, category=category)
        ProductFactory(name='NC Quantum', manufacturer=biotronic, category=category)

    def test_add_new_rebate(self):
        self.visit_reverse('admin:price_rebate_add')
        self.wait_for_element_contains_text('#content h1', 'Add rebate')
        self.assertEqual(len(self.find_elements('#rebatable_items-group, #rebatable_items-2-group')), 0)
        self.wait_for_element_contains_text('.field-status', 'New')

        self.click_save_and_continue()
        self.wait_for_error_message('Please correct the errors below.')
        self.wait_for_element_contains_text('.field-name .errorlist', 'This field is required.')
        self.wait_for_element_contains_text('.field-manufacturer .errorlist', 'This field is required.')
        self.wait_for_element_contains_text('.field-client .errorlist', 'This field is required.')

        self.fill_form_field_with_text('name', 'Marketshare rebate')
        self.select_option('select#id_manufacturer', 'Medtronik')
        self.select_option('select#id_client', 'Children Hospital')
        self.fill_form_field_with_text('start_date', '2018-05-06')
        self.click_save_and_continue()

        self.wait_for_success_message('The rebate "Marketshare rebate: 2018-05-06 - None" was added successfully.')
        self.assertEqual(len(self.find_elements('#rebatable_items-group, #rebatable_items-2-group')), 2)
        self.find_element('#rebatable_items-group tr.add-row td a').click()
        self.assert_elements_count('tr#rebatable_items-0 .field-object_id select option', 0)

        self.select_option('#id_rebatable_items-0-content_type', 'product')
        self.wait_for_element_contains_text('tr#rebatable_items-0 .field-object_id', 'Entrisa')
        self.wait_for_element_contains_text('tr#rebatable_items-0 .field-object_id', 'Apex')
        self.select_option('tr#rebatable_items-0 .field-object_id select', 'Apex')

        self.find_element('#rebatable_items-2-group tr.add-row td a').click()
        self.select_option('#id_rebatable_items-2-0-content_type', 'category')
        self.wait_for_element_contains_text('tr#rebatable_items-2-0 .field-object_id', 'DDD pacemaker')
        self.wait_for_element_contains_text('tr#rebatable_items-2-0 .field-object_id', 'Balloons')
        self.select_option('tr#rebatable_items-2-0 .field-object_id select', 'Balloons')

        self.find_element('#rebatable_items-2-group tr.add-row td a').click()
        self.select_option('#id_rebatable_items-2-1-content_type', 'specialty')
        self.wait_for_element_contains_text('tr#rebatable_items-2-1 .field-object_id', 'CRD')
        self.wait_for_element_contains_text('tr#rebatable_items-2-1 .field-object_id', 'Accessories')
        self.select_option('tr#rebatable_items-2-1 .field-object_id select', 'Accessories')

        self.find_link('Add another Tier').click()
        self.select_option('#id_tier_set-0-tier_type', 'Spend')
        self.fill_form_field_with_text('tier_set-0-upper_bound', '30')

        self.click_save_and_continue()
        self.wait_for_success_message('The rebate "Marketshare rebate: 2018-05-06 - None" was changed successfully.')
        self.assert_option_is_selected('tr#rebatable_items-0 .field-object_id select', 'Apex')
        self.assert_option_is_selected('tr#rebatable_items-2-0 .field-object_id select', 'Balloons')
        self.assert_option_is_selected('tr#rebatable_items-2-1 .field-object_id select', 'Accessories')
        self.wait_for_element_contains_text('#tier_set-0 td.original > p', 'Spend in range (0.00, 30.00)')

        self.find_element('.submit-row input[value="Apply Rebate"]').click()
        self.wait_for_success_message('Marketshare rebate: 2018-05-06 - None successfully set to Complete')
        self.wait_for_element_contains_text('.field-status', 'Complete')

        self.find_element('.submit-row input[value="Unapply Rebate"]').click()
        self.wait_for_success_message('Marketshare rebate: 2018-05-06 - None successfully set to New')
        self.wait_for_element_contains_text('.field-status', 'New')
