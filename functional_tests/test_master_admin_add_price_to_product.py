from device.factories import ProductFactory
from functional_tests.base import MasterAdminTestCase
from hospital.factories import ClientFactory
from price.factories import ClientPriceFactory, DiscountFactory
from price.models import UNIT_COST


class ProductPriceAdminTestCase(MasterAdminTestCase):
    def setUp(self):
        super().setUp()
        self.log_in_master_admin()
        self.product = ProductFactory(name='pacemaker')
        self.client_1, self.client_2 = ClientFactory.create_batch(2)
        client_price = ClientPriceFactory(product=self.product, client=self.client_1, unit_cost=1000, system_cost=1200)
        DiscountFactory(client_price=client_price, cost_type=UNIT_COST, name='CCO', order=1, percent=10)
        DiscountFactory(client_price=client_price, cost_type=UNIT_COST, name='Repless', order=2, percent=15)

        self.visit_reverse('admin:device_product_change', self.product.id)
        self.wait_for_element_contains_text('.app-device.model-product #content h1', 'Change product')

    def assert_cost_table(self, table, header, footer, rows=[]):
        self.assertEqual(self.find_element('thead', parent=table).text, header)
        self.assertEqual(self.find_element('tfoot', parent=table).text, footer)
        discounts = self.find_elements('tbody tr', parent=table)
        for index, discount in enumerate(discounts):
            self.assertEqual(discount.text, rows[index])

    def test_view_existing_prices(self):
        self.assert_elements_count('.inline-related.has_original', 1)
        self.wait_for_element_contains_text('.inline-related.has_original h3 span.inline_label',
                                            f'{self.client_1.name}: Unit Price')

        client_price_section = self.find_element('.inline-related.has_original')
        self.find_element('h3', parent=client_price_section).click()
        price_tables = self.find_elements('table.discounts', parent=client_price_section)
        self.assert_cost_table(price_tables[0],
                               header='UNIT COST $1000.00',
                               footer='Total unit cost $765.00',
                               rows=['Point of Sale CCO 1 -10.00% -$100.00',
                                     'Point of Sale Repless 2 -15.00% -$135.00'])

        self.assert_cost_table(price_tables[1],
                               header='SYSTEM COST $1200.00',
                               footer='Total system cost $1200.00')

    def test_edit_discounts_on_system_cost(self):
        self.find_element('.inline-related.has_original h3').click()
        self.find_element('.field-discounts .system_cost-discounts-table a.related-widget-wrapper-link').click()

        self.browser.switch_to_window(self.browser.window_handles[1])
        self.wait_for_element_contains_text('.model-clientprice #content h1', 'Change client price')
        self.assert_element_attribute_value('#id_system_cost', '1200.00')

        system_cost_discounts = self.find_element('.last-related')
        self.assertEqual(self.find_element('h2', parent=system_cost_discounts).text,
                         'DISCOUNTS ON SYSTEM COST')
        self.fill_form_field_with_text('discount_set-0-percent', 10)
        self.fill_form_field_with_text('discount_set-2-percent', '')

        self.click_submit_button()
        self.wait_for_element_contains_text('.errornote', 'Please correct the error below.')
        self.wait_for_element_contains_text('#discount_set-2 .field-percent .errorlist', 'This field is required.')

        self.select_option('#id_discount_set-2-discount_type', 'Discount by Dollar Value')
        self.click_submit_button()
        self.wait_for_element_contains_text('#discount_set-2 .field-value .errorlist', 'This field is required.')

        self.select_option('#id_discount_set-2-discount_type', 'Discount by percent')
        self.fill_form_field_with_text('discount_set-2-percent', 20)
        self.click_submit_button()
        self.wait_for(lambda: self.assertEqual(len(self.browser.window_handles), 1))
        self.browser.switch_to_window(self.browser.window_handles[0])
        system_cost_table = self.find_element('table.discounts.system_cost-discounts-table')
        self.assert_cost_table(system_cost_table,
                               header='SYSTEM COST $1200.00',
                               footer='Total system cost $840.00',
                               rows=['Preorder Bulk 1 -10.00% -$120.00',
                                     'Point of Sale Repless 1 -20.00% -$240.00'])

    def test_edit_costs(self):
        self.find_element('.inline-related.has_original h3').click()
        self.fill_form_field_with_text('clientprice_set-0-unit_cost', 1200)
        self.fill_form_field_with_text('clientprice_set-0-system_cost', 1000)
        self.click_save_and_continue()
        self.wait_for_success_message('The product "pacemaker" was changed successfully. You may edit it again below.')

        self.find_element('.inline-related.has_original h3').click()
        price_tables = self.find_elements('table.discounts')
        self.assert_cost_table(price_tables[0],
                               header='UNIT COST $1200.00',
                               footer='Total unit cost $918.00',
                               rows=['Point of Sale CCO 1 -10.00% -$120.00',
                                     'Point of Sale Repless 2 -15.00% -$162.00'])
        self.assert_cost_table(price_tables[1],
                               header='SYSTEM COST $1000.00',
                               footer='Total system cost $1000.00')
