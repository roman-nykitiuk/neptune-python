from django.urls import path, include

from hospital.views import ClientListView

app_name = 'hospital'


urlpatterns = [
    path('clients', ClientListView.as_view(), name='clients'),
    path('clients/<int:client_id>/', include('hospital.urls.device', namespace='device')),
    path('clients/<int:client_id>/', include('hospital.urls.order', namespace='order')),
    path('clients/<int:client_id>/', include('hospital.urls.tracker', namespace='tracker')),
]
