from django.shortcuts import render, redirect
from apps.login.api import APIClient
from apps.usuarios.api import APIClient as UsuariosAPIClient
from apps.principal.api import APIClient as APIPrincipalClient
from datetime import date, datetime, timedelta
from django.contrib import messages
from collections import OrderedDict, defaultdict
import random
import json
import os


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
    analistas_activos = len([u for u in users if u.get('estado', '').lower() == 'activo' and u.get('rol', '').lower() == 'analista'])
    
    
    registros_lecturas = api_principal.get_lecturas() or []


    alertas_recientes = 0

    if registros_lecturas:
        hoy = datetime.now().date()
        inicio_semana = hoy - timedelta(days=hoy.weekday())     # lunes
        fin_semana = inicio_semana + timedelta(days=6)          # domingo

        # Campos que deben revisarse
        campos_revision = [
            "ph", "turbidez", "od", "sst", 
            "conductividad", 
            "temperatura_agua", "volumen_agua"
        ]

        for reg in registros_lecturas:

            # Convertimos timestamp a fecha
            try:
                fecha_reg = datetime.fromisoformat(reg["timestamp"]).date()
            except:
                continue

            # Solo contar registros de esta semana
            if not (inicio_semana <= fecha_reg <= fin_semana):
                continue

            punto = reg.get("punto_muestreo")
            biofiltro_id = reg.get("biofiltro_id")

            # --- Entrada nunca cuenta como alerta por biofiltro_id null ---
            if punto == "entrada":
                # pero si tiene otros campos importantes en null → alerta
                if any(reg.get(c) is None for c in campos_revision):
                    alertas_recientes += 1
                continue

            # --- Salida del biofiltro: no debe tener nada en NULL ---
            if punto == "salida_biofiltro":
                if any(reg.get(c) is None for c in campos_revision):
                    alertas_recientes += 1
                continue


    sensores_labels = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    sensores_data = [0, 0, 0, 0, 0, 0, 0]  

    if registros_lecturas:
        hoy = datetime.now().date()
        inicio_semana = hoy - timedelta(days=hoy.weekday())  
        fin_semana = inicio_semana + timedelta(days=6)      

        for reg in registros_lecturas:

            # Convertimos fecha
            try:
                fecha_reg = datetime.fromisoformat(reg["timestamp"]).date()
            except:
                continue

            # Solo datos de esta semana
            if not (inicio_semana <= fecha_reg <= fin_semana):
                continue

            # Día de la semana (0=lunes, 6=domingo)
            dia_idx = fecha_reg.weekday()

            # Sumamos 1 lectura para ese día
            sensores_data[dia_idx] += 1

    alertas_por_planta = {1: 0, 2: 0, 3: 0}

    if registros_lecturas:
        hoy = datetime.now().date()
        inicio_semana = hoy - timedelta(days=hoy.weekday())     # lunes
        fin_semana = inicio_semana + timedelta(days=6)          # domingo

        campos_revision = [
            "ph", "turbidez", "od", "sst", 
            "conductividad", 
            "temperatura_agua", "volumen_agua"
        ]

        for reg in registros_lecturas:

            # Convertir fecha
            try:
                fecha_reg = datetime.fromisoformat(reg["timestamp"]).date()
            except:
                continue

            # Solo esta semana
            if not (inicio_semana <= fecha_reg <= fin_semana):
                continue

            punto = reg.get("punto_muestreo")
            bf_id = reg.get("biofiltro_id")

            # Solo contar salidas del biofiltro 1-3
            if punto == "salida_biofiltro" and bf_id in (1, 2, 3):

                # ¿Falta un campo importante?
                if any(reg.get(c) is None for c in campos_revision):
                    alertas_por_planta[bf_id] += 1

    # Convertir dict → lista en orden correcto
    plantas_labels = ["Hierba del Sapo", "Carrizo Enano", "Papiro Enano"]
    alertas_data = [
        alertas_por_planta[1],
        alertas_por_planta[2],
        alertas_por_planta[3]
    ]

    context = {
        "user": user_info,
        "total_usuarios": total_usuarios,
        "usuarios_activos": usuarios_activos,
        "usuarios_inactivos": usuarios_inactivos,
        "analistas_activos": analistas_activos,
        # Datos inventados
        "alertas_recientes": alertas_recientes,
        "sensores_labels": sensores_labels,
        "sensores_data": sensores_data,
        "plantas_labels": plantas_labels,
        "alertas_data": alertas_data,
    }

    return render(request, "principal/index.html", context)



def agricultor_view(request):
    eficiencia_data = api_principal.get_eficiencia() or []
    
    def color_por_eficiencia(valor):
        """Devuelve color según eficiencia de planta."""
        if valor >= 85:
            return "#34f041cc" 
        elif valor >= 75:
            return "#f0c419cc" 
        else:
            return "#f04334cc"  

    if isinstance(eficiencia_data, list) and eficiencia_data:
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
    eficiencia_data = api_principal.get_eficiencia() or []
    lecturas_data = api_principal.get_lecturas() or []

    ph_actual = temperatura_actual = volumen_diario = ocupantes_actual = 0
    ph_data, turbidez_data, fechas_mes = [], [], []
    historial_diario = []


    if isinstance(lecturas_data, list) and lecturas_data:

        lecturas_salida = [l for l in lecturas_data if l.get("biofiltro_id") == 3]

        # Última lectura GLOBAL (por ID)
        ultima_lectura = max(lecturas_data, key=lambda x: x.get("id", 0))

        # Extraer valores actuales
        ph_actual = ultima_lectura.get("ph", 0)
        temperatura_actual = ultima_lectura.get("temperatura_agua", 0)
        ocupantes_actual = ultima_lectura.get("numero_usuarios", 0)

        # Volumen acumulado total del biofiltro
        volumen_diario = sum(float(l.get("volumen_agua", 0)) for l in lecturas_salida)

        # Datos del último mes para gráficos de pH y turbidez
        hoy = datetime.now().date()
        hace_un_mes = hoy - timedelta(days=30)

        lecturas_mes = [
            l for l in lecturas_data
            if l.get("timestamp")
            and datetime.fromisoformat(l["timestamp"]).date() >= hace_un_mes
        ]

        for l in lecturas_mes:
            fecha = datetime.fromisoformat(l["timestamp"]).strftime("%d/%m")
            ph_data.append(float(l.get("ph", 0)))
            turbidez_data.append(float(l.get("turbidez", 0)))
            fechas_mes.append(fecha)

        #Historial completo (todas las lecturas)
        for l in lecturas_data:
            fecha = datetime.fromisoformat(l["timestamp"]).strftime("%d-%m-%Y")
            historial_diario.append({
                "fecha": fecha,
                "ph": l.get("ph", 0),
                "turbidez": l.get("turbidez", 0),
                "od": l.get("od", 0),
                "ocupantes": l.get("numero_usuarios", 0),
            })


    def color_por_eficiencia(valor):
        if valor >= 85:
            return "#34f041cc"  
        elif valor >= 75:
            return "#f0c419cc"  
        else:
            return "#f04334cc"  

    if isinstance(eficiencia_data, list) and eficiencia_data:

        registros_por_dia = OrderedDict()

        for reg in eficiencia_data:
            try:
                fecha_obj = datetime.strptime(reg["timestamp"], "%Y-%m-%dT%H:%M:%S")
            except (ValueError, KeyError):
                continue

            fecha_dia = fecha_obj.date().isoformat()
            registros_por_dia.setdefault(fecha_dia, reg)

        registros_filtrados = list(registros_por_dia.values())

        # Último registro válido
        ultimo_registro = registros_filtrados[0]

        try:
            ultima_revision = datetime.strptime(
                ultimo_registro["timestamp"], "%Y-%m-%dT%H:%M:%S"
            ).strftime("%d/%m/%Y %H:%M")
        except (ValueError, KeyError):
            ultima_revision = ultimo_registro.get("timestamp", "-")

        cumple_norma = bool(ultimo_registro.get("cumple_norma"))
        estado_agua = "Cumple Norma" if cumple_norma else "No Cumple Norma"
        cumple_norma_color = "#2eed64e8" if cumple_norma else "#f04334e8"

        # Eficiencia por biofiltro
        biofiltros_nombres = ["Hierba del Sapo", "Carrizo Enano", "Papiro Enano"]
        biofiltros = {
            nombre: ultimo_registro.get(f"eficiencia_bf{i+1}_turbidez")
            for i, nombre in enumerate(biofiltros_nombres)
        }

        biofiltros_fallando = [n for n, v in biofiltros.items() if v is None]
        estado_biofiltro = (
            "Funcionando"
            if not biofiltros_fallando
            else f"No Funcionando ({', '.join(biofiltros_fallando)})"
        )

        plantas_validas = [(n, float(v)) for n, v in biofiltros.items() if v is not None]
        planta_eficiente = (
            min(plantas_validas, key=lambda x: x[1])[0] if plantas_validas else "-"
        )

        eficiencia_plantas = [
            {"nombre": nombre, "valor": float(valor), "color": color_por_eficiencia(float(valor))}
            for nombre, valor in biofiltros.items()
            if valor is not None
        ]

        etiquetas, valores, colores = [], [], []

        for reg in reversed(registros_filtrados):
            try:
                fecha = datetime.strptime(reg["timestamp"][:10], "%Y-%m-%d").strftime("%d/%m")
            except (ValueError, KeyError):
                continue

            etiquetas.append(fecha)
            valores.append(float(reg.get("eficiencia_turbidez_global", 0)))
            colores.append(
                "rgba(46, 237, 100, 0.8)"
                if reg.get("cumple_norma")
                else "rgba(240, 67, 52, 0.8)"
            )

    else:
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

        # Datos de lecturas
        "ph_actual": ph_actual,
        "temperatura_actual": temperatura_actual,
        "volumen_diario": volumen_diario,
        "ocupantes_actual": ocupantes_actual,

        # Historial
        "historial_diario": historial_diario,

        # Gráficos
        "ph_chart_labels": fechas_mes,
        "ph_chart_data": ph_data,
        "turbidez_chart_data": turbidez_data,
        "chart_labels": etiquetas,
        "chart_data": valores,
        "chart_colors": colores,
    }

    return render(request, "principal/analista.html", contexto)

def sensors_view(request):
    lecturas_data = api_principal.get_lecturas() or []

    hoy = datetime.now().date()
    lecturas_hoy = [l for l in lecturas_data if datetime.fromisoformat(l["timestamp"]).date() == hoy]

    if lecturas_hoy:
        ultima_lectura = max(lecturas_hoy, key=lambda x: x.get("id", 0))
        ph_actual = ultima_lectura.get("ph", 0)
        temperatura_actual = ultima_lectura.get("temperatura_agua", 0)
        turbidez_actual = ultima_lectura.get("turbidez", 0)
    else:
        ph_actual = temperatura_actual = turbidez_actual = 0

    # Determinar color según rangos
    def color_ph(ph):
        if 6.5 <= ph <= 8.5:
            return "text-green-600", "Dentro del rango"
        elif 6 <= ph < 6.5 or 8.5 < ph <= 9:
            return "text-yellow-500", "Cercano al límite"
        else:
            return "text-red-600", "Fuera de rango"

    def color_temp(temp):
        if 20 <= temp <= 28:
            return "text-green-600", "Normal"
        elif 18 <= temp < 20 or 28 < temp <= 30:
            return "text-yellow-500", "Levemente fuera"
        else:
            return "text-red-600", "Fuera de rango"

    def color_turbidez(turb):
        if turb <= 10:
            return "text-green-600", "Normal"
        elif 10 < turb <= 15:
            return "text-yellow-500", "Levemente alta"
        else:
            return "text-red-600", "Alta"

    ph_color, ph_estado = color_ph(ph_actual)
    temp_color, temp_estado = color_temp(temperatura_actual)
    turb_color, turb_estado = color_turbidez(turbidez_actual)

    contexto = {
        "ph_actual": ph_actual,
        "ph_color": ph_color,
        "ph_estado": ph_estado,
        "temperatura_actual": temperatura_actual,
        "temp_color": temp_color,
        "temp_estado": temp_estado,
        "turbidez_actual": turbidez_actual,
        "turb_color": turb_color,
        "turb_estado": turb_estado,
    }

    return render(request, 'principal/sensors.html', contexto)


def biofilters_view(request):
    lecturas_data = api_principal.get_eficiencia() or []

    # Tomamos los últimos 7 días
    hoy = datetime.today().date()
    semana_pasada = hoy - timedelta(days=6)

    biofiltros = ["Biofiltro A", "Biofiltro B", "Biofiltro C"]
    eficiencia_acumulada = defaultdict(list)

    # === 1️⃣ Recopilar valores de eficiencia por biofiltro ===
    for l in lecturas_data:
        try:
            fecha = datetime.fromisoformat(l["timestamp"]).date()
        except (ValueError, KeyError):
            continue

        if semana_pasada <= fecha <= hoy:
            for i, nombre in enumerate(biofiltros):
                valor = l.get(f"eficiencia_bf{i+1}_turbidez")
                if valor is not None:
                    eficiencia_acumulada[nombre].append(float(valor))

    eficiencia_promedio = []
    for nombre in biofiltros:
        valores = eficiencia_acumulada.get(nombre, [])
        promedio = round(sum(valores) / len(valores), 2) if valores else 0
        eficiencia_promedio.append({"nombre": nombre, "promedio": promedio})

    valores = [p["promedio"] for p in eficiencia_promedio]
    bajadas = []

    for i, valor in enumerate(valores):
        if i == 0:
            bajada = round(100 - valor, 2)
        else:
            bajada = round(valores[i-1] - valor, 2)
        bajadas.append(bajada)

    # Insertar bajada en cada estructura
    for i, bf in enumerate(eficiencia_promedio):
        bf["bajada"] = bajadas[i]

    # === 4️⃣ Ordenar por mejor bajada REAL ===
    eficiencia_ordenada = sorted(eficiencia_promedio, key=lambda x: x["bajada"], reverse=True)

    # === 5️⃣ Asignar color según ranking ===
    for i, bf in enumerate(eficiencia_ordenada):
        if i == 0:
            bf["color_rank"] = "#22c55e"   # 🟩 mejor
        elif i == 1:
            bf["color_rank"] = "#eab308"   # 🟨 segundo
        else:
            bf["color_rank"] = "#ef4444"   # 🟥 peor

    biofiltro_top = eficiencia_ordenada[0] if eficiencia_ordenada else {
        "nombre": "-",
        "promedio": 0,
        "bajada": 0,
        "color_rank": "#ccc"
    }

    contexto = {
        "eficiencia_promedio": eficiencia_ordenada,
        "biofiltro_top": biofiltro_top,
    }

    return render(request, 'principal/biofilters.html', contexto)


def analysis_view(request):
    lecturas_data = api_principal.get_lecturas() or []
    eficiencia_data = api_principal.get_eficiencia() or []

    ph_data, volumen_data, od_data, fechas_semana = [], [], [], []
    pie_labels, pie_values, pie_colors = [], [], []

    hoy = datetime.now().date()
    hace_siete_dias = hoy - timedelta(days=6)

    # Agrupar lecturas por día
    promedios_diarios = defaultdict(lambda: {"ph":0, "volumen":0, "od":0, "count":0})
    for l in lecturas_data:
        ts = l.get("timestamp")
        if not ts:
            continue
        fecha = datetime.fromisoformat(ts).date()
        if fecha < hace_siete_dias:
            continue
        promedios_diarios[fecha]["ph"] += float(l.get("ph", 0))
        promedios_diarios[fecha]["volumen"] += float(l.get("volumen_agua", 0))
        promedios_diarios[fecha]["od"] += float(l.get("od", 0))
        promedios_diarios[fecha]["count"] += 1

    # Nombres de días
    dias_es = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

    # Crear listas
    for i in range(7):
        dia = hace_siete_dias + timedelta(days=i)
        datos = promedios_diarios.get(dia)
        fechas_semana.append(dias_es[dia.weekday()])
        if datos and datos["count"] > 0:
            ph_data.append(round(datos["ph"]/datos["count"],2))
            volumen_data.append(round(datos["volumen"]/datos["count"],2))
            od_data.append(round(datos["od"]/datos["count"],2))
        else:
            ph_data.append(0)
            volumen_data.append(0)
            od_data.append(0)

    if isinstance(eficiencia_data, list) and eficiencia_data:
        ultima = max(eficiencia_data, key=lambda x: x.get("id", 0))

        valores = [
            float(ultima.get("eficiencia_bf1_turbidez", 0)),
            float(ultima.get("eficiencia_bf2_turbidez", 0)),
            float(ultima.get("eficiencia_bf3_turbidez", 0))
        ]

        nombres = ["Hierba del Sapo", "Carrizo Enano", "Papiro Enano"]

        bajadas = [
            round(100 - valores[0], 2),           # A
            round(valores[0] - valores[1], 2),    # B
            round(valores[1] - valores[2], 2)     # C
        ]

        # Ordenar para ranking visual
        orden = sorted(
            zip(nombres, bajadas),
            key=lambda x: x[1],
            reverse=True
        )

        # Asignar colores según ranking
        ranking_colors = ["#10B981", "#FBBF24", "#EF4444"]  # verde, amarillo, rojo

        pie_labels = [o[0] for o in orden]
        pie_values = [o[1] for o in orden]
        pie_colors = ranking_colors[:len(orden)]

    contexto = {
        "ph_chart_labels": fechas_semana,
        "ph_chart_data": ph_data,
        "volume_chart_data": volumen_data,
        "od_chart_data": od_data,
        "pie_chart_labels": pie_labels,
        "pie_chart_data": pie_values,
        "pie_chart_colors": pie_colors,
    }

    return render(request, "principal/analysis.html", contexto)

def history_view(request):
    """
    Historial: gráficos de pH y volumen del último mes + tabla resumen semanal
    """
    lecturas_data = api_principal.get_lecturas() or []

    hoy = datetime.now().date()
    hace_un_mes = hoy - timedelta(days=30)

    # Filtramos lecturas del último mes
    lecturas_mes = [
        l for l in lecturas_data
        if l.get("timestamp") and datetime.fromisoformat(l["timestamp"]).date() >= hace_un_mes
    ]

    lecturas_mes.sort(key=lambda x: x.get("timestamp", ""))

    # Datos para gráficos diarios
    ph_data, volumen_data, dias_labels = [], [], []

    for l in lecturas_mes:
        fecha = datetime.fromisoformat(l["timestamp"]).strftime("%d/%m")
        dias_labels.append(fecha)
        ph_data.append(float(l.get("ph", 0)))
        volumen_data.append(float(l.get("volumen_agua", 0)))

    # Datos para resumen semanal
    semanas = defaultdict(list)
    for l in lecturas_mes:
        fecha_obj = datetime.fromisoformat(l["timestamp"]).date()
        semana_num = fecha_obj.isocalendar()[1]  # número de semana ISO
        semanas[semana_num].append(l)

    resumen_semanal = []
    for semana, lecturas in sorted(semanas.items()):
        if not lecturas:
            continue
        ph_prom = round(sum(float(l.get("ph",0)) for l in lecturas)/len(lecturas),2)
        vol_prom = round(sum(float(l.get("volumen_agua",0)) for l in lecturas)/len(lecturas),2)
        od_prom = round(sum(float(l.get("od",0)) for l in lecturas)/len(lecturas),2)
        resumen_semanal.append({
            "semana": f"Semana {semana}",
            "ph_promedio": ph_prom,
            "volumen_promedio": vol_prom,
            "od_promedio": od_prom
        })

    contexto = {
        "ph_history_labels": dias_labels,
        "ph_history_data": ph_data,
        "volume_history_data": volumen_data,
        "resumen_semanal": resumen_semanal
    }

    return render(request, 'principal/history.html', contexto)


def predictions_view(request):
    lecturas = api_principal.get_lecturas() or []
    hoy = datetime.now().date()

    # Filtrar solo lecturas de "entrada" del día actual
    lecturas_entrada_hoy = [
        l for l in lecturas
        if l.get("punto_muestreo") == "entrada"
        and l.get("timestamp")[:10] == hoy.isoformat()
    ]

    if not lecturas_entrada_hoy:
        return render(request, 'principal/predictions.html', {
            "error": "No hay lecturas de entrada registradas hoy."
        })

    # Tomar las últimas 10 lecturas
    lecturas_entrada_hoy = sorted(lecturas_entrada_hoy, key=lambda x: x["timestamp"])[-10:]

    resultados = []

    for lectura in lecturas_entrada_hoy:
        datos_envio = {
            "conductividad_entrada": lectura.get("conductividad"),
            "numero_usuarios": lectura.get("numero_usuarios"),
            "od_entrada": lectura.get("od"),
            "ph_entrada": lectura.get("ph"),
            "sst": lectura.get("sst"),
            "temperatura_agua": lectura.get("temperatura_agua"),
            "turbidez_entrada": lectura.get("turbidez"),
            "volumen_agua_entrada": lectura.get("volumen_agua"),
        }


        resultado = api_principal.predicciones(datos_envio)

        resultados.append({
            "timestamp": lectura.get("timestamp"),
            "datos": datos_envio,
            "prediccion": resultado
        })

    # Guardar predicciones localmente (opcional)
    archivo_predicciones = os.path.join("data", "predicciones.json")
    os.makedirs("data", exist_ok=True)
    with open(archivo_predicciones, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)


    # Convertir listas a JSON válido antes de pasarlas al template
    labels = json.dumps([r["timestamp"] for r in resultados])
    prob_vals = json.dumps([
        r["prediccion"].get("probabilidad_cumplimiento", 0)
        if isinstance(r["prediccion"], dict) else 0
        for r in resultados
    ])
    cumple_vals = json.dumps([
        1 if isinstance(r["prediccion"], dict) and r["prediccion"].get("prediccion_cumple_norma") else 0
        for r in resultados
    ])

    # Render del template
    return render(request, 'principal/predictions.html', {
        "resultados": resultados,
        "labels": labels,
        "prob_vals": prob_vals,
        "cumple_vals": cumple_vals
    })
