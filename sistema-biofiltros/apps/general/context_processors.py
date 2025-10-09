# apps/general/context_processors.py
from datetime import datetime
from apps.login.api import APIClient

api = APIClient()

def sidebar_user(request):
    token = request.session.get('api_token')
    expiry = request.session.get('token_expiry')

    if not token or not expiry or datetime.utcnow().timestamp() > expiry:
        return {"user": None}  # No hay usuario válido

    api.token = token

    try:
        user_info = api.me()
    except Exception:
        user_info = None

    return {"user": user_info}
