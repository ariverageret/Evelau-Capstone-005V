from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from apps.login.api import APIClient

api = APIClient()

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

        # Obtener info del usuario para conocer el rol
        api.token = result['access_token']
        user_info = api.me()
        role = user_info.get("rol", "").lower()  # adaptalo según cómo venga en tu API

        messages.success(request, f"Login exitoso como {role}")

        # Redirección según rol
        if role == "admin":
            return redirect("principal_home")
        elif role == "analista":
            return redirect("analista_home")
        elif role == "agricultor":
            return redirect("agricultor")
        else:
            return redirect("login")  # si el rol no está definido

    # Si ya hay token, verificar expiración
    token = request.session.get('api_token')
    expiry = request.session.get('token_expiry')
    if token and expiry:
        if datetime.utcnow().timestamp() < expiry:
            # Obtener info del usuario para conocer el rol
            api.token = token
            user_info = api.me()
            role = user_info.get("rol", "").lower()
            
            # Redirección según rol
            if role == "administrador":
                return redirect("principal_home")
            elif role == "analista":
                return redirect("analista_home")
            elif role == "supervisor":
                return redirect("supervisor_home")
            else:
                request.session.flush()
                return redirect("login")
        else:
            # Token expirado
            request.session.flush()

    return render(request, "login/login.html")

def logout_view(request):
    # Limpiar toda la sesión
    request.session.flush()
    messages.success(request, "Has cerrado sesión correctamente")
    return redirect("login")