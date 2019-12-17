from calendar import month_name
from datetime import datetime

from django.db.models import Sum
from knox.auth import TokenAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from device.constants import ProductLevel
from device.models import Category
from device.serializers import CategorySerializer
from hospital.models import Client, Item
from hospital.permissions import IsClientPhysician
from price.models import SYSTEM_COST, UNIT_COST
from tracker.models import PurchasePrice
from tracker.serializers import PurchasePriceSerializer, ClientAPPSerializer, PhysicianAPPSerializer, \
    ManufacturerAPPSerializer, SavingSerializer


class PurchasePriceMixin(object):
    @staticmethod
    def get_purchase_price(client_id, category_id, level, cost):
        client = get_object_or_404(Client, pk=client_id)
        category = get_object_or_404(Category, pk=category_id)

        product_level = ProductLevel.to_value(level)
        cost_type = UNIT_COST if cost == 'unit_cost' else SYSTEM_COST
        kwargs = dict(category=category, client=client, level=product_level,
                      cost_type=cost_type, year=datetime.utcnow().year)
        purchase_price, created = PurchasePrice.objects.get_or_create(**kwargs)
        if created:
            purchase_price.update_prices()
        return purchase_price


class PurchasePriceView(PurchasePriceMixin, APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsClientPhysician)

    def get(self, request, client_id, category_id, level, cost):
        purchase_price = self.get_purchase_price(client_id, category_id, level, cost)
        return Response(PurchasePriceSerializer(purchase_price).data)


class PhysicianAPPView(PurchasePriceMixin, APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsClientPhysician)

    def get(self, request, client_id, category_id, level, cost):
        """
        Get current physician APP analysis at a client, and break down by manufactures
        """
        purchase_price = self.get_purchase_price(client_id, category_id, level, cost)
        physician = purchase_price.client.account_set.get(user=request.user)
        items = Item.objects.filter(
            device__product__category=purchase_price.category,
            device__product__level=purchase_price.level,
            cost_type=purchase_price.cost_type,
            cost__gt=0
        ).used_by_physician(physician).used_in_period(purchase_price.year)

        try:
            physician_app = PhysicianAPPSerializer(items.physician_app()[0]).data
        except IndexError:
            physician_app = None

        return Response({
            'client': ClientAPPSerializer(purchase_price).data,
            'physician': physician_app,
            'manufacturers': ManufacturerAPPSerializer(items.marketshare(), many=True).data,
        })


class PhysicianCategoryListView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsClientPhysician)

    def get(self, request, client_id):
        """
        Get a list of categories of devices used by current physician at the client
        """
        client = get_object_or_404(Client, pk=client_id)
        physician = client.account_set.get(user=request.user)
        categories = Category.objects.filter(
            product__device__client=client,
            product__device__item__is_used=True,
            product__device__item__rep_case__physician=physician
        ).distinct()
        return Response(CategorySerializer(categories, many=True).data)


class PhysicianSavingView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsClientPhysician)

    def get(self, request, client_id, procedure_date=''):
        """
        Get current physician saving analysis at a client
        """
        try:
            procedure_time = datetime.strptime(procedure_date, '%Y-%m')
        except ValueError:
            procedure_time = datetime.utcnow()

        month = procedure_time.month
        year = procedure_time.year
        client = get_object_or_404(Client, pk=client_id)
        physician = get_object_or_404(request.user.account_set, client=client)
        client_annual_items = Item.objects.used_by_client(client).used_in_period(year)
        client_monthly_items = client_annual_items.used_in_period(year, month)
        physician_annual_items = client_annual_items.used_by_physician(physician)

        return Response([{
            'name': f'{month_name[month]} {year} savings',
            'client': client_monthly_items.aggregate(saving=Sum('saving'))['saving'],
            'physician': client_monthly_items.used_by_physician(physician).aggregate(saving=Sum('saving'))['saving'],
        }, {
            'name': f'{year} savings',
            'client': client_annual_items.aggregate(saving=Sum('saving'))['saving'],
            'physician': physician_annual_items.aggregate(saving=Sum('saving'))['saving'],
            'categories': SavingSerializer(physician_annual_items.saving_by_categories(), many=True).data
        }])
