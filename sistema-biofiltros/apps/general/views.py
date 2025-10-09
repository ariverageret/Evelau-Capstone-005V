from django.shortcuts import render, redirect
from apps.login.api import APIClient
from datetime import datetime

api = APIClient()

def data_user(request):
    token = request.session.get('api_token')
    expiry = request.session.get('token_expiry')
    if not token or not expiry or datetime.utcnow().timestamp() > expiry:
        # Token no existe o expiró
        request.session.flush()
        return redirect("login")
    api.token = token
    user_info = api.me()
    print(user_info)
    return render(request, "principal/index.html", {"user": user_info})
