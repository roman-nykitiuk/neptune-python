from device.factories import CategoryFactory, ProductFactory
from functional_tests.base import MasterAdminTestCase


class FeatureAdminTestCase(MasterAdminTestCase):
    def setUp(self):
        super().setUp()
        self.log_in_master_admin()
        self.category = CategoryFactory(name='Implant System')
        self.product = ProductFactory(name="LINQ", category=self.category)

    def test_add_new_features(self):
        # Add a new category feature
        self.visit_reverse('admin:device_category_change', self.category.id)
        self.wait_for_element_contains_text('#content h1', 'Change category')
        self.find_link('Add another Category feature').click()
        self.fill_form_field_with_text('categoryfeature_set-0-name', 'Dimension')
        self.click_save_and_continue()
        self.wait_for_success_message('The category "Implant System" was changed successfully.')

        # Go to product page to add new features
        self.visit_reverse('admin:device_product_change', self.product.id)
        self.wait_for_element_contains_text('#content h1', 'Change product')

        # Dimension must be displayed in FEATURES
        self.assert_elements_count('#feature_set-group table tr.form-row:not(.empty-form)', 1)
        self.assert_element_attribute_value('#id_feature_set-0-name', 'Dimension')
        self.fill_form_field_with_text('feature_set-0-value', '12kg')
        self.click_save_and_continue()
        self.wait_for_success_message('The product "LINQ" was changed successfully')
        self.assert_element_attribute_value('#id_feature_set-0-value', '12kg')

        # Add a new feature
        self.find_link('Add another Feature').click()
        self.fill_form_field_with_text('feature_set-1-name', 'Height')
        self.fill_form_field_with_text('feature_set-1-value', '123cm')
        self.click_save_and_continue()
        self.wait_for_success_message('The product "LINQ" was changed successfully')

        self.visit_reverse('admin:device_category_change', self.category.id)
        self.wait_for_element_contains_text('#content h1', 'Change category')
        self.assert_element_attribute_value('#id_categoryfeature_set-1-name', 'Height')
