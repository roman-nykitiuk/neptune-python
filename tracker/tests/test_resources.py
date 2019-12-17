import os

from decimal import Decimal
from django.test import TestCase
from tablib import Dataset

from device.factories import SpecialtyFactory, CategoryFactory
from device.models import ProductLevel
from hospital.factories import ClientFactory
from neptune.settings.base import FIXTURE_DIR
from price.models import UNIT_COST
from tracker.models import PurchasePrice
from tracker.resources import PurchasePriceResource


class PurchasePriceResourceTestCase(TestCase):
    def setUp(self):
        self.client = ClientFactory(name='UVMCdemo')
        specialty = SpecialtyFactory(name='Cardiac Rhythm Management')
        self.category = CategoryFactory(name='DDD Pacemakers', specialty=specialty)

    def test_import_from_xls_file(self):
        purchase_resource = PurchasePriceResource()
        dataset = Dataset().load(open(os.path.join(FIXTURE_DIR, 'purchaseprice.xls'), 'rb').read())
        purchase_resource.import_data(dataset)

        self.assertEqual(PurchasePrice.objects.count(), 1)
        imported_purchase_price = PurchasePrice.objects.first()
        self.assertEqual(imported_purchase_price.client, self.client)
        self.assertEqual(imported_purchase_price.category, self.category)
        self.assertEqual(imported_purchase_price.year, 2017)
        self.assertEqual(imported_purchase_price.level, ProductLevel.ENTRY.value)
        self.assertEqual(imported_purchase_price.cost_type, UNIT_COST)
        self.assertEqual(imported_purchase_price.avg, Decimal(123))
