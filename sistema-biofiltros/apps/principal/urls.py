from django.urls import path
from .views import principal_home  # debe coincidir con el nombre real

urlpatterns = [
    path('', principal_home, name='principal_home'),
]
