from calendar import month_name
from datetime import datetime

from knox.auth import TokenAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from device.models import Category, Product
from device.schemas import CategorySchema, ProductSchema
from device.serializers import CategorySerializer, ProductSerializer, FeatureSerializer
from hospital.constants import RolePriority
from hospital.models import BULK_PURCHASE, Item
from hospital.serializers import ItemSerializer
from device.serializers import MarketshareSerializer
from price.constants import ON_DOCTOR_ORDER
from price.models import Discount


class CategoryListView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    schema = CategorySchema()

    def get(self, request, client_id):
        """
        List of categories of the logged in user
        """
        client = get_object_or_404(request.user.clients, pk=client_id)
        account = get_object_or_404(client.account_set, user=request.user)
        categories = Category.objects.filter(product__clientprice__client=client,
                                             specialty__in=account.specialties.all()).distinct()
        category_ids = categories.values_list('id', flat=True)
        categories = list(categories) + list(Category.get_all_parent_categories(category_ids))
        category_serializer = CategorySerializer(set(categories), many=True)
        return Response(category_serializer.data)


class ProductListView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    schema = ProductSchema()

    def get(self, request, client_id, category_id):
        """
        List of devices of the category
        """
        client = get_object_or_404(request.user.clients, pk=client_id)
        selected_products = Product.objects.filter(category_id=category_id, enabled=True)
        products = selected_products\
            .prefetch_price_with_discounts(client, discount_apply_types=[ON_DOCTOR_ORDER]) \
            .prefetch_features() \
            .select_related('manufacturer')\
            .unused_bulk_items_count_by_client(client)

        client_inventory_bulk_discounts = Discount.objects.available_in_client_inventory(client).to_client_prices_dict()
        context = {'client_inventory_bulk_discounts': client_inventory_bulk_discounts}
        return Response(ProductSerializer(products, many=True, context=context).data)


class ItemListView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, client_id, product_id):
        client = get_object_or_404(request.user.clients, pk=client_id)
        device = get_object_or_404(client.device_set, product_id=product_id)
        items = device.item_set.filter(purchase_type=BULK_PURCHASE, is_used=False).all()
        return Response(ItemSerializer(items, many=True).data)


class FeatureListView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        features = product.feature_set.filter(value__isnull=False).select_related(
            'category_feature', 'category_feature__shared_image'
        ).all()
        return Response(FeatureSerializer(features, many=True).data)


class PhysicianMarketshareView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, client_id, procedure_date=''):
        try:
            procedure_time = datetime.strptime(procedure_date, '%Y-%m')
        except ValueError:
            procedure_time = datetime.utcnow()

        month = procedure_time.month
        year = procedure_time.year
        physician = get_object_or_404(request.user.account_set,
                                      role__priority=RolePriority.PHYSICIAN.value,
                                      client_id=client_id)
        monthly_marketshare = Item.objects.used_by_physician(physician).used_in_period(year, month).marketshare()
        annual_marketshare = Item.objects.used_by_physician(physician).used_in_period(year).marketshare()

        return Response([
            {
                'name': f'{month_name[month]}, {year}',
                'marketshare': MarketshareSerializer(monthly_marketshare, many=True).data
            }, {
                'name': f'{year} to Date',
                'marketshare': MarketshareSerializer(annual_marketshare, many=True).data
            }
        ])
