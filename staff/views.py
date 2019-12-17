from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from device.models import Manufacturer, Product
from hospital.models import Client, Device
from price.constants import ON_DOCTOR_ORDER
from staff.serializers import AccountSerializer, ProductSerializer, EntrySerializer, DeviceSerializer, \
    ItemSerializer


class AccountListAPIView(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def get(self, request, client_id):
        """
        List all active users of a client
        """
        client = get_object_or_404(Client, pk=client_id)
        accounts = client.account_set.order_by('role__name').all().select_related('role', 'user')
        return Response(AccountSerializer(accounts, many=True).data)


class DiscountListAPIView(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def get(self, request, client_id):
        """
        List all discounts of a client
        """
        client = get_object_or_404(Client, pk=client_id)
        products = Product.objects.filter(clientprice__client=client).distinct()\
            .prefetch_price_with_discounts(client, discount_apply_types=[ON_DOCTOR_ORDER])
        return Response(ProductSerializer(products, many=True).data)


class DeviceListAPIView(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def get(self, request, client_id):
        """
        List all devices of a client
        """
        client = get_object_or_404(Client, pk=client_id)
        devices = client.device_set.select_related('product',
                                                   'product__category',
                                                   'product__category__specialty',
                                                   'product__manufacturer')
        return Response(DeviceSerializer(devices, many=True).data)


class ItemListAPIView(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def get(self, request, device_id):
        """
        List all items of a device
        """
        device = get_object_or_404(Device, pk=device_id)
        items = device.item_set.filter(is_used=False)
        return Response(ItemSerializer(items, many=True).data)


class ManufacturerEntryListView(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser)

    def get(self, request, manufacturer_id, model_name):
        manufacturer = get_object_or_404(Manufacturer, pk=manufacturer_id)
        entries = manufacturer.rebatable_items(model_name)
        return Response(EntrySerializer(entries, many=True).data)
