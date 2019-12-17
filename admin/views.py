from datetime import datetime, timedelta

from knox.auth import TokenAuthentication
from knox.views import LoginView
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.authentication import CredentialsAuthentication
from api.schema import LoginSchema

from device.serializers import MarketshareSerializer
from hospital.constants import BULK_PURCHASE, RolePriority
from hospital.models import Client, Item
from hospital.permissions import HasAdminAccess, IsClientAdmin
from hospital.serializers import PhysicianSerializer
from order.models import Order
from order.serializers import OrderSummarySerializer
from tracker.serializers import RepcaseItemSerializer, SavingsSerializer


class AdminLoginAPIView(LoginView):
    """
    post:
    User login by email/password
    """
    authentication_classes = (CredentialsAuthentication,)
    permission_classes = (HasAdminAccess,)
    schema = LoginSchema()


class AdminAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsClientAdmin)


class OrderSummaryBySpecialtyListAPIView(AdminAPIView):
    def get(self, request, client_id):
        """
        Summarize number of orders of:
            + current client (by all physicians)
            + per specialty ordered by all physicians
        """
        client = get_object_or_404(Client, pk=client_id)
        client_orders = Order.objects.filter(physician__client=client)

        return Response({
            'client': {
                'id': client.id,
                'name': client.name,
                'count': client_orders.count()
            },
            'specialties': OrderSummarySerializer(client_orders.count_by_specialty(), many=True).data
        })


class ClientMarketshareAPIView(AdminAPIView):
    def get(self, request, client_id):
        client = get_object_or_404(Client, pk=client_id)
        year = datetime.utcnow().year
        annual_marketshare = Item.objects.used_by_client(client).used_in_period(year).marketshare()

        return Response({
            'name': f'{year} Year to Date',
            'marketshare': MarketshareSerializer(annual_marketshare, many=True).data
        })


class TodayCasesAPIView(AdminAPIView):
    def get(self, request, client_id):
        """
        List today's cases at current client
        """
        client = get_object_or_404(Client, pk=client_id)
        today = datetime.utcnow().date()
        items = client.items.filter(rep_case__procedure_date=today).select_related(
            'rep_case__physician__user',
            'device__product__manufacturer',
            'device__product__category',
            'device__product',
        )
        return Response(RepcaseItemSerializer(items, many=True).data)


class SavingsAPIView(AdminAPIView):
    def get(self, request, client_id, year=''):
        """
        Year to date savings of the current client
        """
        try:
            given_year = datetime.strptime(year, '%Y').year
        except ValueError:
            given_year = datetime.utcnow().year
        client = get_object_or_404(Client, pk=client_id)
        items = Item.objects.used_by_client(client)
        savings = items.savings_by_month(given_year)
        return Response(SavingsSerializer(savings, many=True).data)


class BulkAPIView(AdminAPIView):
    def get(self, request, client_id):
        """
        Bulk inventory info for current user
        """
        client = get_object_or_404(Client, pk=client_id)
        unused_bulk_items = client.items.filter(is_used=False, purchase_type=BULK_PURCHASE)
        today = datetime.utcnow().date()
        expiring60_date = today + timedelta(days=60)
        expiring30_date = today + timedelta(days=30)
        return Response({
            'available': unused_bulk_items.count(),
            'expiring60': unused_bulk_items.filter(expired_date__lt=expiring60_date,
                                                   expired_date__gte=expiring30_date).count(),
            'expiring30': unused_bulk_items.filter(expired_date__lt=expiring30_date,
                                                   expired_date__gte=today).count(),
            'expired': unused_bulk_items.filter(expired_date__lt=today).count(),
        })


class PhysiciansAPIView(AdminAPIView):
    def get(self, request, client_id):
        """
        List all physicians of the current client
        """
        client = get_object_or_404(Client, pk=client_id)
        physicians = client.account_set.filter(role__priority=RolePriority.PHYSICIAN.value).select_related('user')

        return Response(PhysicianSerializer(physicians, many=True).data)


class SpecialtiesAPIView(AdminAPIView):
    def get(self, request, client_id):
        """
        List all specialties used by the current client
        """
        client = get_object_or_404(Client, pk=client_id)
        specialties = client.items.values_list('device__product__category__specialty__id',
                                               'device__product__category__specialty__name')
        return Response([{'id': specialty_id, 'name': specialty_name} for specialty_id, specialty_name in specialties])
