from rest_framework import serializers

from hospital.models import Account, Client, Item


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('id', 'name', 'image')


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('identifier', 'expired_date', 'purchased_date')


class PhysicianSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name')
    email = serializers.CharField(source='user.email')

    class Meta:
        model = Account
        fields = ('id', 'name', 'email')
