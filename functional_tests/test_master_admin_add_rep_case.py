from datetime import datetime, date

from selenium.webdriver.common.keys import Keys

from account.factories import UserFactory
from device.factories import ProductFactory, ManufacturerFactory
from functional_tests.base import MasterAdminTestCase
from hospital.constants import RolePriority
from hospital.factories import ClientFactory, AccountFactory, RoleFactory, ItemFactory
from hospital.models import Item, Device
from price.constants import PERCENT_DISCOUNT, VALUE_DISCOUNT, PRE_DOCTOR_ORDER, ON_DOCTOR_ORDER
from price.factories import ClientPriceFactory, DiscountFactory
from price.models import SYSTEM_COST, UNIT_COST
from tracker.factories import RepCaseFactory


class RepCaseAdminTestCase(MasterAdminTestCase):
    def setUp(self):
        super().setUp()
        self.log_in_master_admin()
        self.visit_reverse('admin:tracker_repcase_add')
        self.wait_for_element_contains_text('#content h1', 'Add rep case')
        physician = RoleFactory(name='Physician', priority=RolePriority.PHYSICIAN.value)
        admin = RoleFactory(name='Admin', priority=RolePriority.ADMIN.value)
        client = ClientFactory(name='NSINC')
        AccountFactory(user=UserFactory(email='doctor@nsinc.com'), role=physician, client=client)
        AccountFactory(user=UserFactory(email='admin@nsinc.com'), role=admin, client=client)

        client = ClientFactory(name='EA')
        AccountFactory(user=UserFactory(email='admin@ea.com'), role=admin, client=client)

        ClientFactory(name='UVMC')

    def assert_owners_not_found(self):
        self.find_element('.field-owners .select2-selection__rendered').click()
        self.wait_for_element_contains_text('.select2-results__option', 'No results found')

    def test_default_add_view(self):
        self.assert_option_is_selected('select#id_client', '---------')
        self.assert_owners_not_found()
        self.assert_element_attribute_value('input#id_procedure_date', '')
        self.assert_option_is_selected('select#id_status', 'New')

    def test_add_form_submission(self):
        self.click_save_and_continue()
        self.wait_for_error_message()
        self.wait_for_element_contains_text('.field-client .errorlist', 'This field is required.')
        self.wait_for_element_contains_text('.field-owners .errorlist', 'This field is required.')
        self.wait_for_element_contains_text('.field-physician .errorlist', 'This field is required')
        self.wait_for_element_contains_text('.field-procedure_date .errorlist', 'This field is required.')

        self.select_option('select#id_client', 'EA')
        self.wait_for_element_contains_text('.field-owners', 'admin@ea.com')

        self.select_option('select#id_client', 'UVMC')
        self.wait_for(lambda: self.assert_elements_count('.field-owners select#id_owners > option', 0))
        self.assert_owners_not_found()

        self.select_option('select#id_client', 'NSINC')
        self.wait_for_element_contains_text('.field-owners', 'admin@nsinc.com')
        self.select_option('select#id_owners', 'admin@nsinc.com')
        self.select_option('select#id_owners', 'doctor@nsinc.com')
        self.select_option('select#id_physician', 'doctor@nsinc.com')
        self.find_link('Today').click()
        self.click_save_and_continue()
        rep_case = f'New case at NSINC on {datetime.utcnow().date()}'
        self.wait_for_success_message(f'The rep case "{rep_case}" was added successfully. You may edit it again below.')
        self.wait_for_element_contains_text('.field-client', 'NSINC')
        self.assert_options_are_selected('select#id_owners', ['admin@nsinc.com', 'doctor@nsinc.com'])
        self.assert_option_is_selected('select#id_physician', 'doctor@nsinc.com')


class RepCaseItemsAdminTestCase(MasterAdminTestCase):
    def setUp(self):
        super().setUp()
        self.log_in_master_admin()

        self.client = ClientFactory(name='NSINC')
        self.product_1 = ProductFactory(name='Accolade VR', manufacturer=ManufacturerFactory(short_name='MDT'))
        self.product_2 = ProductFactory(name='Evera MRI XT', manufacturer=ManufacturerFactory(short_name='BIO'))
        ClientPriceFactory(
            client=self.client, product=self.product_1, system_cost=100, discounts=[
                DiscountFactory(name='CCO', cost_type=SYSTEM_COST, discount_type=PERCENT_DISCOUNT, percent=20, order=2,
                                apply_type=ON_DOCTOR_ORDER),
                DiscountFactory(name='Repless', cost_type=SYSTEM_COST, discount_type=VALUE_DISCOUNT, value=20, order=1,
                                apply_type=ON_DOCTOR_ORDER),
            ]
        )

        bulk_discount = DiscountFactory(name='Bulk', cost_type=UNIT_COST, discount_type=VALUE_DISCOUNT, value=50,
                                        order=1, apply_type=PRE_DOCTOR_ORDER)
        ClientPriceFactory(
            client=self.client, product=self.product_2, unit_cost=200, discounts=[
                DiscountFactory(name='Repless', cost_type=UNIT_COST, percent=10, order=1, apply_type=ON_DOCTOR_ORDER),
                bulk_discount
            ]
        )
        device = Device.objects.get(client=self.client, product=self.product_2)
        item = ItemFactory(device=device, is_used=False, serial_number='SER1234', discounts=[bulk_discount],
                           cost_type=UNIT_COST, purchased_date=date(2018, 1, 1))
        self.assertEqual(item.cost, 150)

        physician = AccountFactory(role=RoleFactory(priority=RolePriority.PHYSICIAN.value), client=self.client)
        self.rep_case = RepCaseFactory(
            client=self.client,
            owners=[physician],
            physician=physician,
            procedure_date=date(2018, 9, 10)
        )
        self.visit_reverse('admin:tracker_repcase_change', self.rep_case.id)
        self.wait_for_element_contains_text('#content h1', 'Change rep case')

    def test_new_repcase_change_view(self):
        self.assert_elements_count('.form-row.has_original', 0)

    def test_add_invalid_item_to_repcase(self):
        self.find_link('Add another Item').click()
        self.assert_elements_count('.form-row.dynamic-item_set', 1)
        self.wait_for(lambda: self.assert_elements_count('#id_item_set-0-discounts select option', 0))

        self.click_save_and_continue()
        self.wait_for_error_message(message='Please correct the error below.')
        self.wait_for_element_contains_text('.field-identifier', 'This field is required.')

    def test_products_and_discounts_for_item(self):
        def assert_created_item(index, **attrs):
            self.assert_option_is_selected(f'#item_set-{index} .item-device > select', attrs['product'])
            self.assert_option_is_selected(f'#item_set-{index} .item-purchase_type > select', attrs['purchase_type'])
            self.assert_option_is_selected(f'#id_item_set-{index}-identifier', attrs['identifier'])
            self.assert_option_is_selected(f'#id_item_set-{index}-cost_type', attrs['cost_type'])
            self.assert_options_are_selected(f'#id_item_set-{index}-discounts', attrs['discounts'])

        self.find_link('Add another Item').click()
        self.assert_elements_count('.form-row.dynamic-item_set', 1)

        self.select_option('.item-specialty > select', self.product_1.category.specialty.name)
        self.select_option('.item-category > select', self.product_1.category.name)
        self.select_option('.item-manufacturer > select', self.product_1.manufacturer.short_name)
        self.select_option('.item-device > select', self.product_1.name)
        self.select_option('.item-purchase_type > select', 'Consignment')

        self.find_element('.item-identifier .select2-container').click()
        self.find_elements('.select2-search__field')[-1].send_keys('Accolade', Keys.ENTER)

        self.select_option('select#id_item_set-0-cost_type', 'System cost')
        self.wait_for_element_contains_text('.field-discounts', 'CCO')
        self.select_option('.field-discounts select', 'CCO')
        self.select_option('.field-discounts select', 'Repless')
        self.select_option('#id_item_set-0-not_implanted_reason', 'Dropped')

        self.find_link('Add another Item').click()
        self.assert_elements_count('.form-row.dynamic-item_set', 2)
        self.select_option('#item_set-1 .item-specialty > select', self.product_2.category.specialty.name)
        self.select_option('#item_set-1 .item-category > select', self.product_2.category.name)
        self.select_option('#item_set-1 .item-manufacturer > select', self.product_2.manufacturer.short_name)
        self.select_option('#item_set-1 .item-device > select', self.product_2.name)
        self.select_option('#item_set-1 .item-identifier select', 'SER1234')
        self.select_option('#item_set-1 .field-discounts select', 'Repless')
        self.select_option('#id_item_set-1-not_implanted_reason', 'Wrong device')
        self.click_save_and_continue()
        self.wait_for_success_message('The rep case "New case at NSINC on 2018-09-10" was changed successfully.')

        self.assert_elements_count('.form-row.has_original', 2)
        assert_created_item(0, identifier='SER1234', product='Evera MRI XT', cost_type='Unit cost',
                            purchase_type='Bulk', discounts=['Repless'])

        assert_created_item(1, identifier='Accolade', product='Accolade VR', cost_type='System cost',
                            purchase_type='Consignment', discounts=['CCO', 'Repless'])

        bulk_item = Item.objects.get(identifier='SER1234')
        consignment_item = Item.objects.get(identifier='Accolade')
        self.assertEqual(bulk_item.cost, 130)
        self.assertEqual(bulk_item.get_not_implanted_reason_display(), 'Wrong device')
        self.assertEqual(consignment_item.cost, 64)
        self.assertEqual(consignment_item.get_not_implanted_reason_display(), 'Dropped')

    def test_add_duplicated_serial_number_item(self):
        item = ItemFactory(rep_case=self.rep_case, device=self.client.device_set.get(product=self.product_1))
        ItemFactory(rep_case=self.rep_case, device=self.client.device_set.get(product=self.product_2))
        self.visit_reverse('admin:tracker_repcase_change', self.rep_case.id)
        self.wait_for_element_contains_text('#content h1', 'Change rep case')
        self.assert_elements_count('.form-row.dynamic-item_set', 2)

        self.find_link('Add another Item').click()
        self.select_option('#item_set-2 .item-purchase_type > select', 'Consignment')
        self.find_element('#item_set-2 .item-identifier .select2-container').click()
        self.find_elements('.select2-search__field')[-1].send_keys(item.identifier, Keys.ENTER)
        self.click_save_and_continue()
        self.wait_for_error_message(message='Please correct the error below.')
        self.wait_for_element_contains_text('#item_set-2 .field-identifier',
                                            f'Item with this identifier {item.identifier} exists')

        self.find_element('#item_set-2 .item-identifier .select2-container').click()
        self.find_elements('.select2-search__field')[-1].send_keys('NEW SERIAL', Keys.ENTER)
        self.click_save_and_continue()
        self.wait_for_success_message('The rep case "New case at NSINC on 2018-09-10" was changed successfully.')
        self.assert_elements_count('.form-row.dynamic-item_set', 3)
