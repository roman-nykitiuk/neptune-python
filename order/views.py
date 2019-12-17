from django.db.models import Count
from knox.auth import TokenAuthentication
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from device.models import Product
from hospital.constants import RolePriority
from hospital.models import Client, Account
from hospital.permissions import IsClientPhysician
from order.models import Preference, Order, Question
from order.serializers import QuestionSerializer, OrderSerializer, OrderSummarySerializer, \
    ProductOrderSummarySerializer, PreferenceQuestionSummarySerializer
from order.schemas import OrderSchema


class ProductPreferenceListView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, client_id, product_id):
        """
        List of possible preferences a physician can select when ordering a product
        """

        product = get_object_or_404(Product, id=product_id)
        client = get_object_or_404(Client, id=client_id)
        questions = Preference.get_preferences_by_product_client(product, client)
        questions_serializer = QuestionSerializer(questions, many=True)
        return Response(questions_serializer.data)


class OrderListView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    schema = OrderSchema()

    def post(self, request, client_id):
        """
        Physician orders a product in a client
        """
        physician_account = get_object_or_404(request.user.account_set,
                                              client_id=client_id,
                                              role__priority=RolePriority.PHYSICIAN.value)
        request.data['physician'] = physician_account.id
        order_serializer = OrderSerializer(data=request.data)
        if order_serializer.is_valid():
            order_serializer.save()
            return Response(order_serializer.data, status=status.HTTP_201_CREATED)
        return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderSummaryListAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsClientPhysician,)

    def get(self, request, client_id):
        """
        Summarize number of orders of:
            + current client (by all physicians)
            + current physician
            + per category ordered by current physician
        """
        client = get_object_or_404(Client, pk=client_id)
        client_orders = Order.objects.filter(physician__client=client)
        physician_orders = client_orders.filter(physician__user=request.user)

        return Response({
            'client': {
                'id': client.id,
                'name': client.name,
                'count': client_orders.count()
            },
            'physician': {
                'id': request.user.id,
                'name': request.user.name,
                'count': physician_orders.count(),
            },
            'categories': OrderSummarySerializer(physician_orders.count_by_category(), many=True).data
        })


class OrderSummaryByCategoryListAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsClientPhysician,)

    def get(self, request, client_id, category_id):
        """
        Summarize number of orders of current physician in a category at a client
        """
        physician = get_object_or_404(Account, client_id=client_id, user=request.user)
        products_with_orders_count = Product.objects.filter(
            order__physician=physician,
            category__id=category_id
        ).annotate(order_count=Count('order__id')).all()

        return Response(ProductOrderSummarySerializer(products_with_orders_count, many=True).data)


class PreferenceByOrderedProductListView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsClientPhysician,)

    def get(self, request, client_id, product_id):
        """
        List of preferences selected by current physician on ordered products
        """
        physician = get_object_or_404(Account, client_id=client_id, user=request.user)
        product = get_object_or_404(Product, pk=product_id)
        questions = Question.objects.annotate(count=Count('id')).filter(order__physician=physician,
                                                                        order__product=product)
        return Response(PreferenceQuestionSummarySerializer(questions, many=True).data)
