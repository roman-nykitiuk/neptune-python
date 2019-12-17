from datetime import date

from decimal import Decimal
from django.test import TestCase

from device.constants import ProductLevel
from device.factories import CategoryFactory, ProductFactory
from hospital.factories import ClientFactory, ItemFactory, DeviceFactory
from price.constants import UNIT_COST
from tracker.factories import RepCaseFactory, PurchasePriceFactory
from tracker.models import PurchasePrice


class RepCaseTestCase(TestCase):
    def setUp(self):
        client = ClientFactory(name='Central Hospital')
        self.rep_case = RepCaseFactory(client=client, procedure_date=date(2020, 10, 30))

    def test_to_string(self):
        self.assertEqual(str(self.rep_case), 'New case at Central Hospital on 2020-10-30')


class PurchasePriceTestCase(TestCase):
    def setUp(self):
        self.purchase_price = PurchasePriceFactory(category=CategoryFactory(name='TAVR'),
                                                   client=ClientFactory(name='EA'),
                                                   avg=Decimal(1000),
                                                   level=ProductLevel.ENTRY.value,
                                                   year=2018)

    def test_to_string(self):
        self.assertEqual(str(self.purchase_price), 'TAVR - EA - Entry level - Unit cost: $1000')

    def test_update_prices(self):
        product = ProductFactory(level=self.purchase_price.level,
                                 category=self.purchase_price.category)
        device = DeviceFactory(client=self.purchase_price.client, product=product)
        item_1, item_2 = ItemFactory.create_batch(2, device=device, is_used=True, cost_type=UNIT_COST, cost=100)
        item_3, item_4 = ItemFactory.create_batch(2, device=device, is_used=True, cost_type=UNIT_COST, cost=400)
        RepCaseFactory(procedure_date=date(2018, 1, 2), items=[item_1, item_2])
        RepCaseFactory(procedure_date=date(2018, 12, 11), items=[item_3])

        self.purchase_price.update_prices()
        self.assertEqual(self.purchase_price.min, item_1.cost)
        self.assertEqual(self.purchase_price.max, item_3.cost)
        self.assertEqual(self.purchase_price.avg, (item_1.cost + item_2.cost + item_3.cost) / 3)

    def test_class_method_update_purchase_price(self):
        def update_client_purchase_price():
            PurchasePrice.update(category=self.purchase_price.category,
                                 client=self.purchase_price.client,
                                 year=self.purchase_price.year,
                                 level=self.purchase_price.level,
                                 cost_type=self.purchase_price.cost_type)
            self.purchase_price.refresh_from_db()

        self.assertEqual(self.purchase_price.avg, Decimal(1000))
        self.assertIsNone(self.purchase_price.min)
        self.assertEqual(self.purchase_price.max, 0)

        update_client_purchase_price()
        self.assertEqual(self.purchase_price.avg, Decimal(0))
        self.assertIsNone(self.purchase_price.min)
        self.assertEqual(self.purchase_price.max, 0)

        item = ItemFactory(cost_type=self.purchase_price.cost_type, is_used=True,
                           device=DeviceFactory(client=self.purchase_price.client,
                                                product=ProductFactory(category=self.purchase_price.category,
                                                                       level=self.purchase_price.level)))
        rep_case = RepCaseFactory(procedure_date=date(2017, 12, 31), items=[item])
        update_client_purchase_price()
        self.assertEqual(self.purchase_price.avg, Decimal(0))
        self.assertIsNone(self.purchase_price.min)
        self.assertEqual(self.purchase_price.max, 0)

        rep_case.procedure_date = date(2018, 1, 1)
        rep_case.save()
        update_client_purchase_price()
        self.assertEqual(self.purchase_price.avg, item.cost)
        self.assertEqual(self.purchase_price.min, item.cost)
        self.assertEqual(self.purchase_price.max, item.cost)
