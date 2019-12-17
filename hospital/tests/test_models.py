from datetime import date
from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from account.factories import UserFactory
from device.factories import SpecialtyFactory, CategoryFactory, ProductFactory
from hospital.factories import ClientFactory, RoleFactory, AccountFactory, DeviceFactory, ItemFactory
from hospital.models import Client, Item
from price.factories import ClientPriceFactory, DiscountFactory
from price.constants import UNIT_COST, SYSTEM_COST, VALUE_DISCOUNT, PERCENT_DISCOUNT, PRE_DOCTOR_ORDER, ON_DOCTOR_ORDER
from tracker.factories import RepCaseFactory


class ClientTestCase(TestCase):
    def setUp(self):
        self.client = ClientFactory()

    def test_to_string_returns_client_name(self):
        self.assertEqual(str(self.client), self.client.name)

    def test_devices_by_specialties(self):
        specialty1, specialty2 = SpecialtyFactory.create_batch(2)
        category1 = CategoryFactory(specialty=specialty1)
        category2, category3 = CategoryFactory.create_batch(2, specialty=specialty2)
        product1 = DeviceFactory(client=self.client, product=ProductFactory(name='Device1', category=category1)).product
        product2 = DeviceFactory(client=self.client, product=ProductFactory(name='Device2', category=category2)).product
        product3 = DeviceFactory(client=self.client, product=ProductFactory(name='Device3', category=category3)).product

        self.assertDictEqual(self.client.devices_by_specialties(), {
            specialty1.id: {'name': specialty1.name, 'products': [(product1.id, product1.name)]},
            specialty2.id: {'name': specialty2.name, 'products': [(product2.id, product2.name),
                                                                  (product3.id, product3.name)]}
        })

    def test_set_children(self):
        hospital1, hospital2, hospital22, hospital222, hospital3, hospital33 = ClientFactory.create_batch(6)
        self.assertIsNone(hospital1.parent)
        self.assertIsNone(hospital2.parent)
        self.assertIsNone(hospital22.parent)
        self.assertIsNone(hospital222.parent)
        self.assertIsNone(hospital3.parent)
        self.assertIsNone(hospital33.parent)

        def _refresh_all_clients():
            hospital_list = [hospital1, hospital2, hospital22, hospital222, hospital3, hospital33]
            return [Client.objects.get(pk=h.id) for h in hospital_list]

        hospital2.set_children(children_ids=[hospital22.id])
        hospital22.set_children(children_ids=[hospital222.id])
        self.client.set_children(children_ids=[hospital1.id, hospital2.id])
        hospital3.set_children(children_ids=[hospital33.id])
        hospital1, hospital2, hospital22, hospital222, hospital3, hospital33 = _refresh_all_clients()

        self.assertEqual(hospital1.parent, self.client)
        self.assertEqual(hospital2.parent, self.client)
        self.assertEqual(hospital22.parent, hospital2)
        self.assertEqual(hospital222.parent, hospital22)
        self.assertIsNone(hospital3.parent)
        self.assertEqual(hospital33.parent, hospital3)

        self.assertEqual(hospital1.root_parent_id, self.client.id)
        self.assertEqual(hospital2.root_parent_id, self.client.id)
        self.assertEqual(hospital22.root_parent_id, self.client.id)
        self.assertEqual(hospital222.root_parent_id, self.client.id)
        self.assertEqual(hospital3.root_parent_id, hospital3.id)
        self.assertEqual(hospital33.root_parent_id, hospital3.id)

        self.client.set_children(children_ids=[hospital1.id, hospital3.id])
        hospital1, hospital2, hospital22, hospital222, hospital3, hospital33 = _refresh_all_clients()

        self.assertEqual(hospital1.parent, self.client)
        self.assertEqual(hospital3.parent, self.client)
        self.assertIsNone(hospital2.parent)
        self.assertEqual(hospital22.parent, hospital2)
        self.assertEqual(hospital222.parent, hospital22)
        self.assertEqual(hospital33.parent, hospital3)

        self.assertEqual(hospital1.root_parent_id, self.client.id)
        self.assertEqual(hospital2.root_parent_id, hospital2.id)
        self.assertEqual(hospital22.root_parent_id, hospital2.id)
        self.assertEqual(hospital222.root_parent_id, hospital2.id)
        self.assertEqual(hospital3.root_parent_id, self.client.id)
        self.assertEqual(hospital33.root_parent_id, self.client.id)


class DeviceTestCase(TestCase):
    def test_to_string_returns_device_name(self):
        device = DeviceFactory(product=ProductFactory(name='Product name'))
        self.assertEqual(str(device), 'Product name')


class RoleTestCase(TestCase):
    def test_role_to_string(self):
        role = RoleFactory()
        self.assertEqual(str(role), role.name)


class AccountTestCase(TestCase):
    def test_account_to_string(self):
        account = AccountFactory(user=UserFactory(email='abc@ea.com'), role=RoleFactory(name='admin'))
        self.assertEqual(str(account), 'admin abc@ea.com')


class ItemTestCase(TestCase):
    def test_item_to_string(self):
        expired_date = timezone.datetime.strptime('2018-12-01', '%Y-%m-%d').date()
        device = DeviceFactory(hospital_number='12345')
        item = ItemFactory(serial_number='SERIAL-ABCD', expired_date=expired_date, device=device)
        self.assertEqual(str(item), f'12345: SERIAL-ABCD expired on 2018-12-01')

    def test_save_method_auto_generate_identifier(self):
        self.assertEqual(ItemFactory(serial_number='Serial-NUMBER', lot_number='LOT').identifier, 'Serial-NUMBER')

        ItemFactory(lot_number='ITEM-LOT', serial_number='')
        next_item = ItemFactory(serial_number=None, lot_number='LOT')
        self.assertTrue(next_item.identifier.startswith('LOT-'))

        next_item.serial_number = 'SERIAL-NUMBER-2'
        next_item.lot_number = 'LOT-2'
        next_item.save()
        self.assertEqual(next_item.identifier, 'SERIAL-NUMBER-2')

    def test_save_method_errors(self):
        self.assertRaises(AttributeError, ItemFactory, serial_number=None, lot_number=None)

        item = ItemFactory()
        self.assertRaises(IntegrityError, Item.objects.create, serial_number=item.serial_number)

    def test_update_cost(self):
        client = ClientFactory()
        product = ProductFactory()
        discount_1 = DiscountFactory(cost_type=UNIT_COST, value=10, discount_type=VALUE_DISCOUNT,
                                     apply_type=PRE_DOCTOR_ORDER)
        discount_2 = DiscountFactory(cost_type=SYSTEM_COST, percent=20, discount_type=PERCENT_DISCOUNT,
                                     apply_type=ON_DOCTOR_ORDER)
        client_price = ClientPriceFactory(product=product, client=client,
                                          unit_cost=100, system_cost=150,
                                          discounts=[discount_1, discount_2])
        device = client.device_set.get(product=product)
        unit_item = ItemFactory(device=device, cost_type=UNIT_COST, purchased_date=date(2017, 9, 8))
        system_item = ItemFactory(device=device, cost_type=SYSTEM_COST,
                                  is_used=True, rep_case=RepCaseFactory(procedure_date=date(2018, 7, 9)))
        item = ItemFactory(cost=1000)

        unit_item.update_cost(discounts=[])
        system_item.update_cost(discounts=[])
        item.update_cost(discounts=[])
        self.assertEqual((unit_item.cost, unit_item.saving), (client_price.unit_cost, 0))
        self.assertEqual((system_item.cost, system_item.saving), (client_price.system_cost, 0))
        self.assertEqual((item.cost, item.saving), (item.cost, 0))

        unit_item.update_cost(discounts=[discount_1, discount_2])
        system_item.update_cost(discounts=[discount_1, discount_2])
        item.update_cost(discounts=[discount_1, discount_2])
        self.assertEqual((unit_item.cost, unit_item.saving), (Decimal('90.00'), 0))
        self.assertEqual((system_item.cost, system_item.saving), (Decimal('120.00'), 30))
        self.assertEqual((item.cost, item.saving), (Decimal('1000.00'), 0))

    def test_property_discounts_as_table(self):
        discount_1, discount_2, discount_3 = DiscountFactory.create_batch(3)
        item = ItemFactory(discounts=[discount_1, discount_2])
        discounts_table = item.discounts_as_table
        self.assertTrue(discount_1.name in discounts_table)
        self.assertTrue(discount_2.name in discounts_table)
        self.assertFalse(discount_3.name in discounts_table)
