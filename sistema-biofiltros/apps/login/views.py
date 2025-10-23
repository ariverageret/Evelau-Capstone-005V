from django.shortcuts import render, redirect
from django.contrib import messages
from .api import APIClient

api = APIClient()

from datetime import datetime, timedelta

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        result = api.login(username, password)
        print("Resultado de login:", result)

        if "error" in result:
            messages.error(request, "Usuario o contraseña inválidos")
            return redirect("login")

        # Guardar token y hora de expiración
        request.session['api_token'] = result['access_token']
        request.session['token_expiry'] = (datetime.utcnow() + timedelta(hours=2)).timestamp()
        messages.success(request, "Login exitoso")
        return redirect("principal_home")

    # Si ya hay token, verificar expiración
    token = request.session.get('api_token')
    expiry = request.session.get('token_expiry')
    if token and expiry:
        if datetime.utcnow().timestamp() < expiry:
            return redirect("principal_home")
        else:
            # Token expirado
            request.session.flush()

    return render(request, "login/login.html")


def register_view(request):
    return render(request, "login/register.html")