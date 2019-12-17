from django.utils.translation import gettext_lazy as _
from enum import Enum


class ProductLevel(Enum):
    UNASSIGNED = 0
    ENTRY = 1
    ADVANCED = 2

    @staticmethod
    def default():
        return ProductLevel.UNASSIGNED

    @staticmethod
    def to_value(level_string):
        try:
            return ProductLevel[level_string.upper()].value
        except KeyError:
            return ProductLevel.UNASSIGNED.value

    @staticmethod
    def to_field_choices():
        return [(item.value, _(str(item))) for item in ProductLevel]

    def __str__(self):
        return f'{self.name.capitalize()} level'


MAX_SUB_CATEGORIES_LEVEL = 5
