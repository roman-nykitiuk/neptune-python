from django.urls import include, path

from tracker.views import PhysicianSavingView

app_name = 'tracker'


urlpatterns = [
    path('app/', include('hospital.urls.app', namespace='app')),
    path('saving', PhysicianSavingView.as_view(), name='saving'),
    path('saving/<str:procedure_date>', PhysicianSavingView.as_view(), name='saving_by_date'),
]
