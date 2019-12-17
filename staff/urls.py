from django.urls import path, re_path

from staff.views import AccountListAPIView, DiscountListAPIView, ManufacturerEntryListView, DeviceListAPIView, \
    ItemListAPIView

app_name = 'staff'
urlpatterns = [
    path('clients/<int:client_id>/accounts', AccountListAPIView.as_view(), name='accounts'),
    path('clients/<int:client_id>/discounts', DiscountListAPIView.as_view(), name='discounts'),
    path('clients/<int:client_id>/devices', DeviceListAPIView.as_view(), name='devices'),
    path('devices/<int:device_id>/items', ItemListAPIView.as_view(), name='items'),
    re_path('^manufacturers/(?P<manufacturer_id>\d+)/(?P<model_name>(product|category|specialty))/?$',
            ManufacturerEntryListView.as_view(), name='rebatable_items'),
]
