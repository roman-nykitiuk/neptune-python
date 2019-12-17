from django.test import TestCase

from hospital.converter import int_to_b32
from hospital.constants import PRODUCT_ITEM_INDENTIFIER_SIZE


class ConverterTestCase(TestCase):
    def test_int_to_b32(self):
        self.assertEqual(int_to_b32(1, 3), '001')
        self.assertEqual(int_to_b32(1, PRODUCT_ITEM_INDENTIFIER_SIZE), '000001')
        self.assertEqual(int_to_b32(1234, 4), '016I')
