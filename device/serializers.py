from rest_framework import serializers

from device.models import Category, Product, Manufacturer, Feature
from price.constants import UNIT_COST, SYSTEM_COST
from price.serializers import DiscountSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'image', 'parent_id')


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ('id', 'name', 'short_name', 'image')


class FeatureSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Feature
        fields = ('id', 'name', 'value', 'image', 'category_feature')

    def get_image(self, feature):
        shared_image = feature.category_feature.shared_image
        return shared_image and shared_image.image.url


class ProductSerializer(serializers.ModelSerializer):
    manufacturer = ManufacturerSerializer()
    unit_cost = serializers.SerializerMethodField()
    system_cost = serializers.SerializerMethodField()
    bulk = serializers.IntegerField()
    features = FeatureSerializer(many=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'image', 'level', 'model_number',
                  'manufacturer', 'bulk',
                  'unit_cost', 'system_cost', 'features')

    @staticmethod
    def _find_max_bulk_discount(bulk_discounts, original_cost):
        max_bulk_discount_value = 0
        max_bulk_discount = None
        for bulk_discount in bulk_discounts:
            bulk_discount_value = bulk_discount.get_value(original_cost) or 0
            if bulk_discount_value > max_bulk_discount_value:
                max_bulk_discount = bulk_discount
                max_bulk_discount_value = bulk_discount_value
        return max_bulk_discount

    def get_cost(self, product, cost_type):
        client_price = product.client_prices[0]
        if cost_type == UNIT_COST:
            cost = client_price.unit_cost
            discounts = client_price.unit_discounts
        else:
            cost = client_price.system_cost
            discounts = client_price.system_discounts

        bulk_discounts = self.context['client_inventory_bulk_discounts'].get(client_price.id, {}).get(cost_type, [])
        max_bulk_discount = self._find_max_bulk_discount(bulk_discounts, cost)
        if max_bulk_discount:
            discounts.append(max_bulk_discount)

        return {
            'value': cost,
            'discounts': DiscountSerializer(discounts, many=True).data
        }

    def get_unit_cost(self, product):
        return self.get_cost(product, cost_type=UNIT_COST)

    def get_system_cost(self, product):
        return self.get_cost(product, cost_type=SYSTEM_COST)


class MarketshareSerializer(serializers.Serializer):
    spend = serializers.DecimalField(max_digits=20, decimal_places=2)
    units = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    id = serializers.IntegerField(source='manufacturer_id')

    def get_name(self, marketshare):
        return marketshare.get('manufacturer_short_name') or marketshare.get('manufacturer_name')
