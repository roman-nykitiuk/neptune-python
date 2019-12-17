from import_export import resources, fields

from device.models import Category, ProductLevel
from hospital.models import Client
from price.models import COST_TYPES
from tracker.models import PurchasePrice


class PurchasePriceResource(resources.ModelResource):
    specialty = fields.Field(attribute='category__specialty__name')
    category = fields.Field(attribute='category__name')
    client = fields.Field(attribute='client__name')
    level = fields.Field()
    cost_type = fields.Field()

    class Meta:
        model = PurchasePrice
        fields = ('id', 'category', 'specialty', 'client', 'level', 'year', 'cost_type', 'avg', 'min', 'max')
        export_order = ('id', 'category', 'specialty', 'client', 'level', 'year', 'cost_type', 'avg', 'min', 'max')

    def dehydrate_level(self, obj):
        return obj.get_level_display()

    def dehydrate_cost_type(self, obj):
        return obj.get_cost_type_display()

    def init_instance(self, row=None):
        instance = super().init_instance(row)
        instance.category = Category.objects.get(specialty__name=row.get('specialty'),
                                                 name=row.get('category'))
        instance.client = Client.objects.get(name=row.get('client'))
        for level in ProductLevel:
            if str(level) in row.get('level'):
                instance.level = level.value
        for cost_type, cost_name in COST_TYPES:
            if str(cost_name) in row.get('cost_type'):
                instance.cost_type = cost_type
        return instance
