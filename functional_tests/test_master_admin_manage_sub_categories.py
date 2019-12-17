from device.factories import CategoryFactory, ProductFactory, SpecialtyFactory
from functional_tests.base import MasterAdminTestCase


class SubCategoriesMasterAdminTestCase(MasterAdminTestCase):
    def setUp(self):
        super().setUp()
        self.specialty = SpecialtyFactory()
        self.category_1, self.category_2 = CategoryFactory.create_batch(2, specialty=self.specialty)
        self.log_in_master_admin()
        self.visit_reverse('admin:device_category_add')
        self.wait_for_element_contains_text('.model-category.change-form #content h1', 'Add category')

    def test_invalid_category_form_submission(self):
        self.click_save_and_continue()
        self.wait_for_error_message('Please correct the errors below.')
        self.wait_for_element_contains_text('.field-name .errorlist', 'This field is required.')
        self.wait_for_element_contains_text('.field-specialty .errorlist', 'This field is required.')

    def test_circular_subcategories_assigned(self):
        self.fill_form_field_with_text('name', 'Category group')
        self.select_option('select#id_specialty', self.category_1.specialty.name)
        self.select_option('select#id_sub_categories', self.category_2.name)
        self.select_option('select#id_parent', self.category_2.name)
        self.click_save_and_continue()
        self.wait_for_error_message('Please correct the error below.')
        self.wait_for_element_contains_text('.errorlist.nonfield', 'Circular sub categories assigned.')

    def test_valid_sub_categories_assigned(self):
        self.fill_form_field_with_text('name', 'Category group')
        self.select_option('select#id_specialty', self.category_1.specialty.name)
        self.select_option('select#id_sub_categories', self.category_1.name)
        self.select_option('select#id_parent', self.category_2.name)
        self.click_save_and_continue()
        self.wait_for_success_message('The category "Category group" was added successfully.')
        self.assert_option_is_selected('select#id_sub_categories', self.category_1.name)
        self.assert_option_is_selected('select#id_parent', self.category_2.name)

    def test_sub_categories_listing(self):
        self.category_2.parent = self.category_1
        self.category_2.save()
        ProductFactory.create_batch(2, category=self.category_2)

        self.visit_reverse('admin:device_specialty_changelist')
        self.wait_for_element_contains_text('.model-specialty.change-list #content h1', 'Select specialty to change')
        self.assert_elements_count('#result_list tbody tr .field-specialty_name', count=1)

        self.find_link(self.specialty.name).click()
        self.wait_for_element_contains_text('.model-category.change-list #content h1', 'Select category to change')
        self.assert_elements_count('#result_list tbody tr .field-category_name', count=1)

        self.find_link(self.category_1.name).click()
        self.wait_for_element_contains_text('#result_list tbody tr .field-category_name', self.category_2.name)

        self.find_link(self.category_2.name).click()
        self.wait_for_element_contains_text('.model-product.change-list #content h1', 'Select product to change')
        self.assert_elements_count('#result_list tbody tr .field-name', count=2)
