from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from rest_framework import serializers

from hospital.constants import RolePriority
from hospital.serializers import ClientSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    default_client = ClientSerializer()
    admin_client = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'name', 'default_client', 'admin_client')

    def get_admin_client(self, user):
        admin_client = user.account_set.filter(role__priority=RolePriority.ADMIN.value).first()
        return admin_client and ClientSerializer(admin_client.client).data


class WriteUserSerializer(serializers.ModelSerializer):
    default_client_id = serializers.IntegerField(required=True)

    class Meta:
        model = User
        fields = ('default_client_id',)

    def validate_default_client_id(self, value):
        try:
            self.instance.clients.get(id=value)
            return value
        except ObjectDoesNotExist:
            raise ValidationError('Invalid client.')
