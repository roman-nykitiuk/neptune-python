from django.urls import path

from admin.views import AdminLoginAPIView, OrderSummaryBySpecialtyListAPIView, ClientMarketshareAPIView, \
    TodayCasesAPIView, SavingsAPIView, BulkAPIView, PhysiciansAPIView, SpecialtiesAPIView

app_name = 'admin'


urlpatterns = [
    path('login', AdminLoginAPIView.as_view(), name='login'),
    path('clients/<int:client_id>/ordersummary', OrderSummaryBySpecialtyListAPIView.as_view(),
         name='ordersummary_by_specialty'),
    path('clients/<int:client_id>/marketshare', ClientMarketshareAPIView.as_view(), name='marketshare'),
    path('clients/<int:client_id>/cases', TodayCasesAPIView.as_view(), name='today_cases'),
    path('clients/<int:client_id>/savings', SavingsAPIView.as_view(), name='savings'),
    path('clients/<int:client_id>/savings/<str:year>', SavingsAPIView.as_view(), name='savings_by_year'),
    path('clients/<int:client_id>/bulk', BulkAPIView.as_view(), name='bulk'),
    path('clients/<int:client_id>/physicians', PhysiciansAPIView.as_view(), name='physicians'),
    path('clients/<int:client_id>/specialties', SpecialtiesAPIView.as_view(), name='specialties'),
]
