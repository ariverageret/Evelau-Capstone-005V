from django.urls import path
from .views import login_view, logout_visual_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', login_view, name='login'),  
    path('logout/', logout_visual_view, name='logout'),  
    path('password_reset/',
         auth_views.PasswordResetView.as_view(template_name='login/password_reset.html'),
         name='password_reset'),  # reset de contraseña
]
