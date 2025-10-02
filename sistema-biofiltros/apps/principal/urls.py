from django.urls import path
from .views import principal_home  # debe coincidir con el nombre real
from . import views

urlpatterns = [
    path('', principal_home, name='principal_home'),
     path("agricultor/", views.agricultor_view, name="agricultor"),

]
