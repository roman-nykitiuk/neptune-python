from django.urls import re_path

from tracker.views import PurchasePriceView

urlpatterns = [
    re_path(r'^clients/(?P<client_id>\d+)/categories/(?P<category_id>\d+)/'
            r'(?P<level>(entry|advanced))/(?P<cost>(unit_cost|system_cost))$',
            PurchasePriceView.as_view(), name='category_purchased_cost'),
]
