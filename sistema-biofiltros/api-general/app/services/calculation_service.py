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
    ph = lectura_salida.get("ph")
    if ph is None or not (settings.NORMA_PH_MIN <= ph <= settings.NORMA_PH_MAX):
        return False
    
    if lectura_salida.get("conductividad", float('inf')) > settings.NORMA_CONDUCTIVIDAD_MAX:
        return False
    if lectura_salida.get("turbidez", float('inf')) > settings.NORMA_TURBIDEZ_MAX:
        return False
    if lectura_salida.get("od", -1) < settings.NORMA_OD_MIN:
        return False
        
    return True

def procesar_y_almacenar_eficiencia(db: Session):
    """
    Servicio principal que orquesta el proceso de cálculo con datos reales de la BD
    y marca los registros como procesados para evitar duplicados.
    """
    logger.info("Iniciando job de cálculo de eficiencia...")

    # 1. OBTENER DATOS NO PROCESADOS DE LA BASE DE DATOS
    
    # 1: Añadir filtro para buscar solo registros no procesados]
    lectura_entrada = db.query(LecturaSensor).filter(
        LecturaSensor.punto_muestreo == 'entrada',
        LecturaSensor.computed_eficiencia == False  # Solo buscar lecturas no procesadas
    ).order_by(LecturaSensor.timestamp.desc()).first()

    if not lectura_entrada:
        # Esto ahora es un comportamiento esperado si no hay datos nuevos.
        logger.info("No se encontraron nuevas lecturas de 'entrada' para procesar.")
        return

    ventana_inicio = lectura_entrada.timestamp
    ventana_fin = ventana_inicio + timedelta(minutes=30)

    lecturas_salida_obj = db.query(LecturaSensor).filter(
        LecturaSensor.punto_muestreo == 'salida_biofiltro',
        LecturaSensor.computed_eficiencia == False, # También buscar salidas no procesadas
        LecturaSensor.timestamp.between(ventana_inicio, ventana_fin)
    ).order_by(LecturaSensor.biofiltro_id, LecturaSensor.timestamp.desc()).all()

    lecturas_salida_map = {ls.biofiltro_id: ls for ls in reversed(lecturas_salida_obj)}

    if len(lecturas_salida_map) < 3:
        logger.warning(
            f"Datos insuficientes para la entrada de las {lectura_entrada.timestamp}. "
            f"Se encontraron salidas para {len(lecturas_salida_map)} de 3 biofiltros. Se reintentará en la próxima ejecución."
        )
        return
    
    logger.info(f"Procesando lectura de entrada con timestamp: {lectura_entrada.timestamp}")
    logger.info(f"Lecturas de salida encontradas para biofiltros: {list(lecturas_salida_map.keys())}")

    # 2. CALCULAR EFICIENCIAS 
    bf1 = lecturas_salida_map.get(1)
    bf2 = lecturas_salida_map.get(2)
    bf3 = lecturas_salida_map.get(3)
    eficiencia_turbidez_bf1 = calcular_eficiencia(lectura_entrada.turbidez, bf1.turbidez)
    eficiencia_turbidez_bf2 = calcular_eficiencia(lectura_entrada.turbidez, bf2.turbidez)
    eficiencia_turbidez_bf3 = calcular_eficiencia(lectura_entrada.turbidez, bf3.turbidez)
    od_salida_promedio = (bf1.od + bf2.od + bf3.od) / 3
    eficiencia_od_global = round(od_salida_promedio - lectura_entrada.od, 2) if lectura_entrada.od is not None else None
    turbidez_salida_promedio = (bf1.turbidez + bf2.turbidez + bf3.turbidez) / 3
    eficiencia_turbidez_global = calcular_eficiencia(lectura_entrada.turbidez, turbidez_salida_promedio)

    # 3. VERIFICAR CUMPLIMIENTO 
    salida_promedio_sistema = {
        "od": od_salida_promedio,
        "ph": (bf1.ph + bf2.ph + bf3.ph) / 3,
        "conductividad": (bf1.conductividad + bf2.conductividad + bf3.conductividad) / 3,
        "turbidez": turbidez_salida_promedio,
    }
    cumple_norma = verificar_cumplimiento_norma(salida_promedio_sistema)
    
    # 4. PREPARAR Y GUARDAR DATOS 
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
    
    # Guardar tanto el nuevo registro de eficiencia como las actualizaciones de las lecturas
    db.commit()
    
    logger.success(f"Cálculo de eficiencia completado y guardado. Lecturas marcadas como procesadas.")