from django.shortcuts import render, redirect
from apps.login.api import APIClient
from datetime import datetime

api = APIClient()

def principal_home(request):
    token = request.session.get('api_token')
    expiry = request.session.get('token_expiry')
    if not token or not expiry or datetime.utcnow().timestamp() > expiry:
        # Token no existe o expiró
        request.session.flush()
        return redirect("login")

    api.token = token
    user_info = api.me()
    return render(request, "principal/index.html", {"user": user_info})

from datetime import datetime


from django.shortcuts import render

def agricultor_view(request):
    contexto = {
        "estado_agua": "Agua Apta",
        "mensaje_estado": "Todos los parámetros dentro del rango",
        "nivel_oxigeno": 8.5,
        "claridad": 94,
        "temperatura": 22,
        "ultima_medicion": datetime.now().strftime("%d/%m/%Y, %H:%M"),
        "estado_biofiltro": "Sistema Activo",
        "historico": [
            {"fecha": "01/10", "oxigeno": 8.4, "claridad": 92},
            {"fecha": "02/10", "oxigeno": 8.3, "claridad": 91},
            {"fecha": "03/10", "oxigeno": 8.4, "claridad": 93},
            {"fecha": "04/10", "oxigeno": 8.5, "claridad": 94},
            {"fecha": "05/10", "oxigeno": 8.6, "claridad": 95},
            {"fecha": "06/10", "oxigeno": 8.5, "claridad": 96},
            {"fecha": "07/10", "oxigeno": 8.4, "claridad": 94},
        ],
        "norma_cumplida": (
            "El agua analizada cumple con todos los parámetros establecidos "
            "en la normativa de calidad para uso agrícola. Los niveles de "
            "oxígeno disuelto, claridad y pH se encuentran dentro de los "
            "rangos óptimos para irrigación de cultivos."
        ),
    }
    return render(request, "principal/agricultor.html", contexto)