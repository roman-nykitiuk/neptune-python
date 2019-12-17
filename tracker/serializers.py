from django.db.models.fields.files import ImageFieldFile, ImageField
from rest_framework import serializers

from hospital.models import Item
from tracker.models import PurchasePrice


class PurchasePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasePrice
        fields = ('avg', 'min', 'max')


class ClientAPPSerializer(serializers.ModelSerializer):
    app = serializers.DecimalField(source='avg', decimal_places=2, max_digits=20)
    id = serializers.IntegerField(source='client.id')
    name = serializers.CharField(source='client.name')

    class Meta:
        model = PurchasePrice
        fields = ('id', 'name', 'min', 'max', 'app')


class PhysicianAPPSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='physician_id')
    name = serializers.CharField(source='physician_name')
    app = serializers.DecimalField(decimal_places=2, max_digits=20)


class ManufacturerAPPSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='manufacturer_id')
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    app = serializers.DecimalField(decimal_places=2, max_digits=20)

    def get_name(self, item):
        return item.get('manufacturer_short_name') or item.get('manufacturer_name')

    def get_image(self, item):
        image_name = item.get('manufacturer_image')
        if image_name:
            return ImageFieldFile(instance=None, field=ImageField(), name=image_name).url


class SavingSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='category_id')
    name = serializers.CharField(source='category_name')
    saving = serializers.DecimalField(max_digits=20, decimal_places=2)
    percent = serializers.SerializerMethodField()

    def get_percent(self, obj):
        percent = 0
        if obj.get('spend'):
            percent = obj.get('saving') * 100 / obj.get('spend')
        return f'{percent:.2f}'


class RepcaseItemSerializer(serializers.ModelSerializer):
    purchase_type = serializers.CharField(source='get_purchase_type_display')
    physician = serializers.CharField(source='rep_case.physician.user.name')
    manufacturer = serializers.CharField(source='device.product.manufacturer.display_name')
    category = serializers.CharField(source='device.product.category.name')
    product = serializers.CharField(source='device.product.name')
    model_number = serializers.CharField(source='device.product.model_number')

    class Meta:
        model = Item
        fields = ('id', 'identifier', 'purchase_type',
                  'physician', 'manufacturer', 'category', 'product', 'model_number')


class SavingsSerializer(serializers.Serializer):
    month = serializers.IntegerField(source='month.month')
    savings = serializers.DecimalField(max_digits=20, decimal_places=2)
    spend = serializers.DecimalField(max_digits=20, decimal_places=2)
    percent = serializers.SerializerMethodField()

    def get_percent(self, obj):
        percent = 0
        if obj.get('spend'):
            percent = obj.get('savings') * 100 / obj.get('spend')
        return f'{percent:.2f}'
