from django.urls import path, re_path

from tracker.views import PurchasePriceView, PhysicianCategoryListView, PhysicianAPPView

app_name = 'app'


urlpatterns = [
    path('categories', PhysicianCategoryListView.as_view(), name='categories'),
    re_path(r'^categories/(?P<category_id>\d+)/(?P<level>(entry|advanced))/(?P<cost>(unit_cost|system_cost))/physician',
            PhysicianAPPView.as_view(), name='physician_app'),
    re_path(r'^categories/(?P<category_id>\d+)/(?P<level>(entry|advanced))/(?P<cost>(unit_cost|system_cost))/?',
            PurchasePriceView.as_view(), name='purchase_price'),
]
