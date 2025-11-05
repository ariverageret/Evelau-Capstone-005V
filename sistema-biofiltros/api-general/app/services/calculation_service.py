from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from decimal import Decimal
from loguru import logger 

# Importar la configuración centralizada
from app.core.config import settings

# Importar los modelos ORM de la base de datos
from app.models.sensor import LecturaSensor # Asumo que tu modelo se llama así
from app.models.eficiencia import EficienciaInstantanea
from app.schemas.eficiencia import EficienciaCreate # Importamos el schema

def calcular_eficiencia(valor_entrada: float, valor_salida: float) -> Optional[Decimal]:
    if valor_entrada is None or valor_salida is None or valor_entrada == 0:
        return None
    eficiencia = ((valor_entrada - valor_salida) / valor_entrada) * 100
    return Decimal(str(round(eficiencia, 2)))

def verificar_cumplimiento_norma(lectura_salida: Dict) -> bool:
    """
    Verifica si una lectura de salida cumple con TODOS los parámetros de la NCh 1333.
    """
    ph = lectura_salida.get("ph")
    if ph is None or not (settings.NORMA_PH_MIN <= ph <= settings.NORMA_PH_MAX):
        logger.warning(f"Incumplimiento de Norma: pH ({ph}) fuera de rango.")
        return False
    
    conductividad = lectura_salida.get("conductividad", float('inf'))
    if conductividad > settings.NORMA_CONDUCTIVIDAD_MAX:
        logger.warning(f"Incumplimiento de Norma: Conductividad ({conductividad}) excede el máximo.")
        return False

    turbidez = lectura_salida.get("turbidez", float('inf'))
    if turbidez > settings.NORMA_TURBIDEZ_MAX:
        logger.warning(f"Incumplimiento de Norma: Turbidez ({turbidez}) excede el máximo.")
        return False

    od = lectura_salida.get("od", -1)
    if od < settings.NORMA_OD_MIN:
        logger.warning(f"Incumplimiento de Norma: Oxígeno Disuelto ({od}) por debajo del mínimo.")
        return False

    # --- MODIFICACIÓN: Añadir validación para SST ---
    # Asumiremos que tu modelo LecturaSensor tiene un campo 'sst'.
    # Si el campo se llama 'solidos_suspendidos_totales', usa ese nombre aquí.
    sst = lectura_salida.get("sst", float('inf'))
    if sst > settings.NORMA_SST_MAX:
        logger.warning(f"Incumplimiento de Norma: SST ({sst}) excede el máximo.")
        return False
        
    logger.info("Todos los parámetros cumplen con la norma NCh 1333.")
    return True

def procesar_y_almacenar_eficiencia(db: Session):
    """
    Servicio principal que orquesta el proceso de cálculo para un sistema SECUENCIAL (en serie)
    y marca los registros como procesados.
    """
    logger.info("Iniciando job de cálculo de eficiencia (Lógica SECUENCIAL)...")

    # 1. OBTENER DATOS NO PROCESADOS (Esta parte no cambia)
    lectura_entrada = db.query(LecturaSensor).filter(
        LecturaSensor.punto_muestreo == 'entrada',
        LecturaSensor.computed_eficiencia == False
    ).order_by(LecturaSensor.timestamp.desc()).first()

    if not lectura_entrada:
        logger.info("No se encontraron nuevas lecturas de 'entrada' para procesar.")
        return

    ventana_inicio = lectura_entrada.timestamp
    ventana_fin = ventana_inicio + timedelta(minutes=30)
    lecturas_salida_obj = db.query(LecturaSensor).filter(
        LecturaSensor.punto_muestreo == 'salida_biofiltro',
        LecturaSensor.computed_eficiencia == False,
        LecturaSensor.timestamp.between(ventana_inicio, ventana_fin)
    ).order_by(LecturaSensor.biofiltro_id, LecturaSensor.timestamp.desc()).all()
    lecturas_salida_map = {ls.biofiltro_id: ls for ls in reversed(lecturas_salida_obj)}
    
    if len(lecturas_salida_map) < 3:
        logger.warning(f"Datos insuficientes para la entrada de las {lectura_entrada.timestamp}. Se reintentará.")
        return
    
    logger.info(f"Procesando entrada de las {lectura_entrada.timestamp} con sus 3 salidas secuenciales.")

    # --- 2. CALCULAR EFICIENCIAS (LÓGICA SECUENCIAL MODIFICADA) ---
    bf1 = lecturas_salida_map.get(1) # Salida de la etapa 1
    bf2 = lecturas_salida_map.get(2) # Salida de la etapa 2
    bf3 = lecturas_salida_map.get(3) # Salida FINAL del sistema

    # Eficiencia por etapa (cada etapa usa la salida anterior como su entrada)
    eficiencia_turbidez_bf1 = calcular_eficiencia(lectura_entrada.turbidez, bf1.turbidez)
    eficiencia_turbidez_bf2 = calcular_eficiencia(bf1.turbidez, bf2.turbidez) # Entrada es bf1
    eficiencia_turbidez_bf3 = calcular_eficiencia(bf2.turbidez, bf3.turbidez) # Entrada es bf2

    # Eficiencia GLOBAL (desde la entrada inicial hasta la salida final)
    eficiencia_turbidez_global = calcular_eficiencia(lectura_entrada.turbidez, bf3.turbidez)
    
    # Ganancia de Oxígeno Disuelto GLOBAL
    eficiencia_od_global = round(bf3.od - lectura_entrada.od, 2) if lectura_entrada.od is not None and bf3.od is not None else None

    # --- 3. VERIFICAR CUMPLIMIENTO (LÓGICA SECUENCIAL MODIFICADA) ---
    # La norma se evalúa ÚNICAMENTE con la salida del último biofiltro (bf3)
    salida_final_sistema = {
        "od": bf3.od,
        "ph": bf3.ph,
        "conductividad": bf3.conductividad,
        "turbidez": bf3.turbidez,
        "sst": bf3.sst
    }
    cumple_norma = verificar_cumplimiento_norma(salida_final_sistema)
    logger.info(f"Evaluación de cumplimiento basada en la salida final (Biofiltro 3). Resultado: {cumple_norma}")
    
    # --- 4. PREPARAR Y GUARDAR DATOS (Esta parte no cambia) ---
    logger.info("Preparando datos de eficiencia para guardar en la BD...")
    datos_eficiencia = EficienciaCreate(
        timestamp=datetime.now(),
        eficiencia_od_global=Decimal(str(eficiencia_od_global)) if eficiencia_od_global is not None else None,
        eficiencia_turbidez_global=eficiencia_turbidez_global,
        eficiencia_bf1_turbidez=eficiencia_turbidez_bf1,
        eficiencia_bf2_turbidez=eficiencia_turbidez_bf2,
        eficiencia_bf3_turbidez=eficiencia_turbidez_bf3,
        cumple_norma=cumple_norma,
    )
    
    db_eficiencia = EficienciaInstantanea(**datos_eficiencia.dict())
    db.add(db_eficiencia)
    
    logger.info("Marcando lecturas de sensores como procesadas...")
    lectura_entrada.computed_eficiencia = True
    for biofiltro_id in lecturas_salida_map:
        lecturas_salida_map[biofiltro_id].computed_eficiencia = True
    
    db.commit()
    
    logger.success(f"Cálculo (secuencial) completado y guardado. Cumple Norma: {cumple_norma}. Lecturas marcadas como procesadas.")