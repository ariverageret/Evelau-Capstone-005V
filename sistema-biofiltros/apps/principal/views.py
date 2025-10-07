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
    # --- Estado principal del agua ---
    estado_agua = "Agua Apta"
    color_estado_agua = "#10B981"  # verde
    estado_agua_emoji = "✅"

    # --- Última revisión ---
    ultima_revision = datetime.now().strftime("%d-%m-%Y %H:%M")

    # --- Estado de biofiltros ---
    estado_biofiltro = "Funcionando"
    estado_biofiltro_emoji = "🟢"

    # --- Planta más eficiente ---
    planta_eficiente = "Carrizo Enano"

    # --- Cumplimiento norma ---
    cumple_norma = "Sí"
    if cumple_norma == "Sí":
        color_norma = "#10B981"  # verde
        norma_emoji = "✅"
    else:
        color_norma = "#EF4444"  # rojo
        norma_emoji = "❌"

    # --- Histórico simplificado de agua por mes ---
    historico_agua = [
        {"mes": "Feb", "estado": "Agua Apta", "color": "green"},
        {"mes": "Mar", "estado": "Agua No Apta", "color": "red"},
        {"mes": "Abr", "estado": "Agua Apta", "color": "green"},
        {"mes": "May", "estado": "Agua con precaución", "color": "yellow"},
        {"mes": "Jun", "estado": "Agua Apta", "color": "green"},
    ]

    # --- Eficiencia de plantas para gráfico de torta ---
    eficiencia_plantas = [
        {"nombre": "Carrizo Enano", "eficiencia": 50, "color": "#10B981"},
        {"nombre": "Papiro Enano", "eficiencia": 30, "color": "#3B82F6"},
        {"nombre": "Hierba de Sapo", "eficiencia": 20, "color": "#F59E0B"},
    ]

    contexto = {
        "estado_agua": estado_agua,
        "color_estado_agua": color_estado_agua,
        "estado_agua_emoji": estado_agua_emoji,
        "ultima_revision": ultima_revision,
        "estado_biofiltro": estado_biofiltro,
        "estado_biofiltro_emoji": estado_biofiltro_emoji,
        "planta_eficiente": planta_eficiente,
        "cumple_norma": cumple_norma,
        "color_norma": color_norma,
        "norma_emoji": norma_emoji,
        "historico_agua": historico_agua,
        "eficiencia_plantas": eficiencia_plantas,
    }

    
    return render(request, "principal/agricultor.html", contexto)