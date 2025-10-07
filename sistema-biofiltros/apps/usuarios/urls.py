from django.urls import path
from .views import mantenedor_usuarios_view, mantenedor_roles_view

urlpatterns = [
    path("", mantenedor_usuarios_view, name="mantenedor_usuarios"),  # ahora será /usuarios/
    path("roles/", mantenedor_roles_view, name="mantenedor_roles"),   # ahora será /usuarios/roles/
]

