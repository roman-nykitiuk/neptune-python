from django.utils.translation import gettext_lazy as _
from django.test import TestCase

from device.constants import ProductLevel


class ProductLevelTestCase(TestCase):
    def test_to_value(self):
        self.assertEqual(ProductLevel.to_value('entry'), ProductLevel.ENTRY.value)
        self.assertEqual(ProductLevel.to_value('wrong'), ProductLevel.UNASSIGNED.value)

    def test_to_string(self):
        self.assertEqual(str(ProductLevel.ENTRY), 'Entry level')

    def test_field_choices(self):
        choices = ProductLevel.to_field_choices()
        self.assertEqual(len(choices), len(list(ProductLevel)))

        choice_value, choice_string = choices[0]
        enum_of_choice = ProductLevel(choice_value)
        self.assertEqual(_(str(enum_of_choice)), choice_string)
