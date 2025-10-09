from django.urls import path
from .views import principal_home  # debe coincidir con el nombre real
from . import views

urlpatterns = [
    path('', principal_home, name='principal_home'),
    path("agricultor/", views.agricultor_view, name="agricultor"),
    path('analista/', views.analista_dashboard, name='analista_dashboard'),
    path('sensors/', views.sensors_view, name='sensors'),     
    path('biofilters/', views.biofilters_view, name='biofilters'),
    path('analysis/', views.analysis_view, name='analysis'),  
    path('history/', views.history_view, name='history'),     
    path('predictions/', views.predictions_view, name='predictions'),
]
