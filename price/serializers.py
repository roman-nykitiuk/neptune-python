from rest_framework import serializers

from price.models import Discount


class DiscountSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Discount
        fields = ('id', 'name', 'value', 'order', 'image', 'percent', 'discount_type', 'apply_type')

    def get_image(self, discount):
        return discount.shared_image and discount.shared_image.image.url
