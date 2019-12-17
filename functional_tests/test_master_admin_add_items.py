from functional_tests.base import MasterAdminTestCase
from hospital.constants import BULK_PURCHASE, CONSIGNMENT_PURCHASE
from hospital.factories import ClientFactory, ItemFactory, DeviceFactory
from price.factories import DiscountFactory


class ItemAdminTestCase(MasterAdminTestCase):
    def setUp(self):
        super().setUp()
        self.log_in_master_admin()
        self.client = ClientFactory()
        self.item_1, self.item_2 = ItemFactory.create_batch(2, device=DeviceFactory(client=self.client),
                                                            is_used=False, purchase_type=BULK_PURCHASE)
        ItemFactory(device=self.item_1.device, is_used=True, purchase_type=BULK_PURCHASE)
        ItemFactory(device=self.item_2.device, is_used=True, purchase_type=CONSIGNMENT_PURCHASE)

    def test_visit_client_inventory(self):
        def assert_item_row(item, row):
            device = item.device
            self.assertEqual(self.find_element('.field-identifier', parent=row).text, item.identifier)
            self.assertEqual(self.find_element('.field-hospital_name', parent=row).text, device.client.name)
            self.assertEqual(self.find_element('.field-manufacturer_name', parent=row).text,
                             item.device.product.manufacturer.name)
            self.assertEqual(self.find_element('.field-hospital_number', parent=row).text, device.hospital_number)
            self.assertEqual(self.find_element('.field-model_number', parent=row).text, device.product.model_number)
            self.assertEqual(self.find_element('.field-serial_number', parent=row).text, item.serial_number)
            self.assertEqual(self.find_element('.field-is_used img', parent=row).get_attribute('alt').lower(),
                             str(item.is_used).lower())

        self.visit_reverse('admin:hospital_client_change', self.client.id)
        self.wait_for_element_contains_text('#content h1', 'Change client')
        self.find_link('Manage bulk serial numbers').click()
        self.wait_for_element_contains_text('#content h1', 'Select item to change')
        self.assert_elements_count('#result_list tbody tr th.field-identifier', count=2)
        assert_item_row(self.item_2, self.find_element('tr.row1'))
        assert_item_row(self.item_1, self.find_element('tr.row2'))

    def test_visit_item_details(self):
        discount = DiscountFactory()
        self.item_1.discounts.add(discount)
        self.visit_reverse('admin:hospital_item_change', self.item_1.id)
        self.wait_for_element_contains_text('.model-item.change-form #content h1', 'Change item')
        self.wait_for_element_contains_text('.field-discounts_details', 'Discounts details:')
        self.assert_elements_count('.field-discounts_details .item-discounts-table tbody tr', 1)
        self.wait_for_element_contains_text('.field-discounts_details .item-discounts-table', discount.name)

        product_name = self.item_1.device.product.name
        self.find_link(product_name).click()
        self.wait_for_element_contains_text('.model-product.change-form #content h1', 'Change product')
        self.assert_element_attribute_value('input#id_name', product_name)
