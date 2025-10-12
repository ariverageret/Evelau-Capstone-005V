from django.shortcuts import render, redirect
from apps.login.api import APIClient
from apps.usuarios.api import APIClient as UsuariosAPIClient
from apps.principal.api import APIClient as APIPrincipalClient
from datetime import datetime
from django.contrib import messages
from collections import OrderedDict


api = APIClient()
usuarios_api = UsuariosAPIClient()
api_principal = APIPrincipalClient()

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
    eficiencia_data = api_principal.get_eficiencia() or []

    def color_por_eficiencia(valor):
        """Devuelve color según eficiencia de planta."""
        if valor >= 85:
            return "#34f041cc"  # verde
        elif valor >= 75:
            return "#f0c419cc"  # amarillo
        else:
            return "#f04334cc"  # rojo

    if isinstance(eficiencia_data, list) and eficiencia_data:
        # 🔹 Agrupar por día y quedarse con el último registro
        registros_por_dia = OrderedDict()
        for reg in eficiencia_data:
            try:
                fecha_obj = datetime.strptime(reg["timestamp"], "%Y-%m-%dT%H:%M:%S")
            except (ValueError, KeyError):
                continue
            fecha_dia = fecha_obj.date().isoformat()
            registros_por_dia.setdefault(fecha_dia, reg)

        registros_filtrados = list(registros_por_dia.values())
        ultimo_registro = registros_filtrados[0]

        # Fecha última revisión
        try:
            ultima_revision = datetime.strptime(ultimo_registro["timestamp"], "%Y-%m-%dT%H:%M:%S")\
                               .strftime("%d/%m/%Y %H:%M")
        except (ValueError, KeyError):
            ultima_revision = ultimo_registro.get("timestamp", "-")

        # Estado agua y color
        cumple_norma = bool(ultimo_registro.get("cumple_norma"))
        estado_agua = "Cumple Norma" if cumple_norma else "No Cumple Norma"
        cumple_norma_color = "#2eed64e8" if cumple_norma else "#f04334e8"

        # Biofiltros
        biofiltros_nombres = ["Hierba del Sapo", "Carrizo Enano", "Papiro Enano"]
        biofiltros = {nombre: ultimo_registro.get(f"eficiencia_bf{i+1}_turbidez") 
                      for i, nombre in enumerate(biofiltros_nombres)}

        biofiltros_fallando = [n for n, v in biofiltros.items() if v is None]
        estado_biofiltro = "Funcionando" if not biofiltros_fallando else f"No Funcionando ({', '.join(biofiltros_fallando)})"

        # Planta más eficiente
        plantas_validas = [(n, float(v)) for n, v in biofiltros.items() if v is not None]
        planta_eficiente = min(plantas_validas, key=lambda x: x[1])[0] if plantas_validas else "-"

        # Eficiencia de cada planta con color
        eficiencia_plantas = [
            {"nombre": nombre, "valor": float(valor), "color": color_por_eficiencia(float(valor))}
            for nombre, valor in biofiltros.items() if valor is not None
        ]

        # Datos para gráfico de barras (último registro de cada día)
        etiquetas, valores, colores = [], [], []
        for reg in reversed(registros_filtrados):  # más antiguo → más reciente
            try:
                fecha = datetime.strptime(reg["timestamp"][:10], "%Y-%m-%d").strftime("%d/%m")
            except (ValueError, KeyError):
                continue
            etiquetas.append(fecha)
            valores.append(float(reg.get("eficiencia_turbidez_global", 0)))
            colores.append("rgba(46, 237, 100, 0.8)" if reg.get("cumple_norma") else "rgba(240, 67, 52, 0.8)")

    else:
        # Si no hay datos
        ultimo_registro = None
        estado_agua = estado_biofiltro = planta_eficiente = "Sin datos"
        cumple_norma = False
        cumple_norma_color = "#cccccc"
        eficiencia_plantas = []
        etiquetas = valores = colores = []
        ultima_revision = "-"

    contexto = {
        "eficiencia_data": eficiencia_data,
        "estado_agua": estado_agua,
        "ultima_revision": ultima_revision,
        "estado_biofiltro": estado_biofiltro,
        "planta_eficiente": planta_eficiente,
        "cumple_norma": "Sí" if cumple_norma else "No",
        "cumple_norma_color": cumple_norma_color,
        "eficiencia_plantas": eficiencia_plantas,
        "chart_labels": etiquetas,
        "chart_data": valores,
        "chart_colors": colores,
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