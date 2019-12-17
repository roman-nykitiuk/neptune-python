from django.urls import path

from order.views import OrderSummaryListAPIView, OrderSummaryByCategoryListAPIView, ProductPreferenceListView
from order.views import OrderListView, PreferenceByOrderedProductListView

app_name = 'order'


urlpatterns = [
    path('orders', OrderListView.as_view(), name='orders'),
    path('orders/products/<int:product_id>/preferences',
         PreferenceByOrderedProductListView.as_view(),
         name='order_preferences'),
    path('ordersummary', OrderSummaryListAPIView.as_view(), name='ordersummary'),
    path('ordersummary/categories/<int:category_id>',
         OrderSummaryByCategoryListAPIView.as_view(), name='ordersummary_by_category'),
    path('preferences/products/<int:product_id>', ProductPreferenceListView.as_view(), name='preferences'),
]
