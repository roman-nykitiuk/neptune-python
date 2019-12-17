from django.urls import path

from device.views import CategoryListView, ProductListView, ItemListView, PhysicianMarketshareView

app_name = 'device'


urlpatterns = [
    path('categories', CategoryListView.as_view(), name='categories'),
    path('categories/<int:category_id>/products', ProductListView.as_view(), name='products'),
    path('products/<int:product_id>/items', ItemListView.as_view(), name='items'),
    path('marketshare', PhysicianMarketshareView.as_view(), name='marketshare'),
    path('marketshare/<str:procedure_date>', PhysicianMarketshareView.as_view(), name='marketshare_by_date'),
]
