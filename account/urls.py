from django.urls import path

from account.views import UserView

app_name = 'account'


urlpatterns = [
    path('user', UserView.as_view(), name='user'),
]
