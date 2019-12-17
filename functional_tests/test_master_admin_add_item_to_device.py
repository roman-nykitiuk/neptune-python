from device.factories import ProductFactory
from hospital.constants import BULK_PURCHASE
from hospital.factories import ClientFactory, ItemFactory
from price.factories import ClientPriceFactory, DiscountFactory
from .base import MasterAdminTestCase


class ItemAdminTestCase(MasterAdminTestCase):
    def setUp(self):
        super().setUp()
        self.log_in_master_admin()
        self.client = ClientFactory()
        self.product = ProductFactory()
        ClientPriceFactory(client=self.client, product=self.product)
        device = self.client.device_set.get(product=self.product)
        self.discounts = DiscountFactory.create_batch(2)
        self.item = ItemFactory(device=device, purchase_type=BULK_PURCHASE, is_used=False, discounts=self.discounts)

    def test_show_client_inventory_for_product(self):
        self.visit_reverse('admin:device_product_change', self.product.id)
        self.wait_for_element_contains_text('#content h1', 'Change product')
        self.assert_elements_count('#clientprice_set-group .has_original', 1)

        self.find_element('#clientprice_set-0').click()
        self.wait_for_element_contains_text('.has_original .field-inventory', 'Bulk: 1 available | 0 used')

        self.find_link('1 available').click()
        self.wait_for(lambda: self.assertEqual(len(self.browser.window_handles), 2))
        self.browser.switch_to_window(self.browser.window_handles[1])
        self.wait_for_element_contains_text('#content h1', 'Change device')
        self.assert_elements_count('.inline-related.has_original.dynamic-item_set', count=1)

        self.find_element('#item_set-0').click()
        self.wait_for_element_contains_text('#item_set-0 .field-discount_details', 'Discount details')
        self.assert_elements_count('#item_set-0 .item-discounts-table tbody tr', count=2)
        self.wait_for_element_contains_text('#item_set-0 .item-discounts-table', self.discounts[0].name)
        self.wait_for_element_contains_text('#item_set-0 .item-discounts-table', self.discounts[1].name)

        self.fill_form_field_with_text(field_name='item_set-0-serial_number', text='')
        self.fill_form_field_with_text(field_name='item_set-0-lot_number', text='')
        self.find_link('Today').click()
        self.click_submit_button()

        self.wait_for_element_contains_text('.errornote', 'Please correct the error below.')
        self.wait_for_element_contains_text('.errorlist.nonfield',
                                            'Either serial number or lot number must be present.')

        self.fill_form_field_with_text('item_set-0-lot_number', 'ITEMLOT')
        self.click_submit_button()

        self.wait_for(lambda: self.assertEqual(len(self.browser.window_handles), 1))
        self.browser.switch_to_window(self.browser.window_handles[0])
        self.find_element('#clientprice_set-0').click()
        self.wait_for_element_contains_text('.has_original .field-inventory', 'Bulk: 1 available | 0 used')
