from rest_framework import serializers

from device.models import Product
from device.serializers import ManufacturerSerializer
from order.models import Order, Question


class QuestionSerializer(serializers.ModelSerializer):
    question = serializers.CharField(source='name')

    class Meta:
        model = Question
        fields = ('id', 'question')


class OrderSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True, source='get_status_display')

    class Meta:
        model = Order
        fields = ('product', 'procedure_datetime', 'cost_type', 'discounts', 'preference_questions', 'physician',
                  'status')


class OrderSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField(source='response_id')
    name = serializers.CharField()
    count = serializers.IntegerField()


class ProductOrderSummarySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    count = serializers.IntegerField(source='order_count')
    name = serializers.CharField()
    manufacturer = ManufacturerSerializer()

    class Meta:
        model = Product
        fields = ('id', 'name', 'count', 'manufacturer')


class PreferenceQuestionSummarySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    count = serializers.IntegerField()
    question = serializers.CharField(source='name')

    class Meta:
        model = Question
        fields = ('id', 'question', 'count')
