from device.factories import SpecialtyFactory, CategoryFactory, ProductFactory
from functional_tests.base import MasterAdminTestCase


class ProductAdminTestCase(MasterAdminTestCase):
    def setUp(self):
        super(ProductAdminTestCase, self).setUp()
        self.log_in_master_admin()
        self.specialty = SpecialtyFactory(name='Cardiac Rhythm Management')
        CategoryFactory.create_batch(2, specialty=self.specialty)

        self.product_1, self.product_2 = ProductFactory.create_batch(2, model_number='1456Q-86')
        ProductFactory.create_batch(3)

    def test_category_select_contains_specialties_as_optgroup(self):
        self.visit_reverse('admin:device_product_add')
        self.wait_for_element_contains_text('#content h1', 'Add product')
        self.browser.execute_script("$('#id_category').select2('open');")
        self.wait_for_element_contains_text(
            '#select2-id_category-results .select2-results__group',
            'Cardiac Rhythm Management'
        )
        specialty_selector = '#select2-id_category-results [aria-label="Cardiac Rhythm Management"]'
        self.assert_elements_count(f'{specialty_selector} li.select2-results__option', 2)

    def test_search_by_product_number(self):
        self.visit_reverse('admin:device_product_changelist')
        self.fill_form_field_with_text('q', self.product_1.model_number)
        self.click_submit_button()
        self.wait_for_element_contains_text('#changelist-search .small', '2 results (5 total)')

    def test_search_by_product_name(self):
        self.visit_reverse('admin:device_product_changelist')
        self.fill_form_field_with_text('q', self.product_2.name)
        self.click_submit_button()
        self.wait_for_element_contains_text('#changelist-search .small', '1 result (5 total)')


class SpecialtyAdminTestCase(MasterAdminTestCase):
    def test_show_list_of_categories(self):
        self.log_in_master_admin()
        self.specialty, specialty = SpecialtyFactory.create_batch(2)
        self.category = CategoryFactory(name='Total Knee System', specialty=self.specialty)
        CategoryFactory.create_batch(2, specialty=specialty)
        ProductFactory.create_batch(3, category=self.category)

        self.visit_reverse('admin:device_specialty_changelist')
        self.wait_for_element_contains_text('#content h1', 'Select specialty to change')
        self.assert_elements_count('#result_list tbody tr', count=2)

        self.find_link(self.specialty.name).click()
        self.wait_for_element_contains_text('#content h1', 'Select category to change')
        self.assert_elements_count('#result_list tbody tr', count=1)
        self.wait_for_element_contains_text('#result_list tbody tr', 'Total Knee System')

        self.find_link(self.category.name).click()
        self.wait_for_element_contains_text('#content h1', 'Select product to change')
        self.assert_elements_count('#result_list tbody tr', count=3)
