from django.urls import path

from device.views import FeatureListView

app_name = 'device'


urlpatterns = [
    path('products/<int:product_id>/features', FeatureListView.as_view(), name='features'),
]
