from django.shortcuts import render, redirect
from apps.login.api import APIClient
from apps.usuarios.api import APIClient as UsuariosAPIClient
from datetime import datetime
from django.contrib import messages

api = APIClient()
usuarios_api = UsuariosAPIClient()

def principal_home(request):
    # Verificar token
    token = request.session.get('api_token')
    expiry = request.session.get('token_expiry')
    if not token or not expiry or datetime.utcnow().timestamp() > expiry:
        request.session.flush()
        return redirect("login")

    api.token = token
    user_info = api.me()

    # Traer usuarios de la API
    result_users = usuarios_api.get_Users()
    if isinstance(result_users, dict) and "error" in result_users:
        messages.error(request, f"Error al obtener usuarios: {result_users['error']}")
        users = []
    else:
        users = result_users

    # Calcular estadísticas
    total_usuarios = len(users) if users else 0
    usuarios_activos = len([u for u in users if u.get('estado', '').lower() == 'activo'])
    usuarios_inactivos = len([u for u in users if u.get('estado', '').lower() != 'activo'])
    analistas_activos = len([u for u in users if u.get('estado', '').lower() == 'activo' and u.get('rol', '').lower() == 'Analista'])

    context = {
        "user": user_info,
        "total_usuarios": total_usuarios,
        "usuarios_activos": usuarios_activos,
        "usuarios_inactivos": usuarios_inactivos,
        "analistas_activos": analistas_activos,
    }

    return render(request, "principal/index.html", context)



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



def analista_dashboard(request):
    """
    Vista para mostrar el dashboard del analista
    """
    return render(request, "principal/analista.html")


def sensors_view(request):
    return render(request, 'principal/sensors.html')

def biofilters_view(request):
    return render(request, 'principal/biofilters.html')

def analysis_view(request):
    return render(request, 'principal/analysis.html')

def history_view(request):
    return render(request, 'principal/history.html')

def predictions_view(request):
    return render(request, 'principal/predictions.html')