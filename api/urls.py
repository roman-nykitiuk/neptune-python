from django.urls import path, include

from api.views import LoginAPIView, LogoutAPIView, LogoutAllAPIView

app_name = 'api'


urlpatterns = [
    path('staff/', include('staff.urls', namespace='staff')),
    path('admin/', include('admin.urls', namespace='admin')),

    path('login', LoginAPIView.as_view(), name='login'),
    path('logout', LogoutAPIView.as_view(), name='logout'),
    path('logout/all', LogoutAllAPIView.as_view(), name='logout_all'),

    path('', include('hospital.urls', namespace='hospital')),
    path('', include('device.urls', namespace='device')),
    path('account/', include('account.urls', namespace='account')),

    # deprecated
    path('', include('api.deprecated_urls'))   # pragma: no cover
]
