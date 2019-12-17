from rest_framework import serializers

from device.models import Product
from hospital.constants import RolePriority
from hospital.models import Account, Item, Device
from price.constants import COST_TYPES, UNIT_COST
from price.models import Discount


class AccountSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name')
    email = serializers.CharField(source='user.email')
    is_physician = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ('id', 'name', 'email', 'is_physician')

    def get_is_physician(self, account):
        return account.role.priority == RolePriority.PHYSICIAN.value


class ItemDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ('id', 'name')


class ProductSerializer(serializers.ModelSerializer):
    discounts = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'discounts')

    def get_discounts(self, product):
        def discounts_by_cost_type(cost_type):
            client_price = product.client_prices[0]
            if cost_type == UNIT_COST:
                return client_price.unit_discounts
            else:
                return client_price.system_discounts

        return dict(
            (cost_type, ItemDiscountSerializer(discounts_by_cost_type(cost_type), many=True).data)
            for cost_type, _ in COST_TYPES
        )


class EntrySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)


class DeviceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='product.name')
    specialty = serializers.CharField(source='product.category.specialty.name')
    category = serializers.CharField(source='product.category.name')
    manufacturer = serializers.CharField(source='product.manufacturer.display_name')
    product = serializers.IntegerField(source='product.id')

    class Meta:
        model = Device
        fields = ('id', 'name', 'specialty', 'category', 'manufacturer', 'product')


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'identifier', 'cost_type')
