import random
from datetime import datetime
from sqlalchemy.orm import Session
from loguru import logger

from app.models.sensor import LecturaSensor # Asegúrate que la importación sea correcta

def generar_lecturas_simuladas(db: Session):
    """
    Simula y guarda un nuevo conjunto de lecturas de sensores (1 entrada, 3 salidas)
    con valores realistas.
    """
    logger.info("Iniciando simulación de datos de sensores...")
    
    # --- 1. Simular condiciones de la vivienda y del agua de ENTRADA ---
    # Valores base para el agua gris "sucia"
    numero_usuarios = random.randint(2, 6)
    temperatura_agua = round(random.uniform(20.0, 26.0), 1)
    
    # La turbidez y conductividad aumentan con el número de usuarios
    turbidez_entrada = random.randint(120, 180) + (numero_usuarios * 5)
    conductividad_entrada = random.randint(1500, 2200) + (numero_usuarios * 20)
    
    # El OD inicial es bajo en aguas grises
    od_entrada = round(random.uniform(1.0, 2.5), 2)
    ph_entrada = round(random.uniform(6.0, 7.5), 1)

    lectura_entrada = LecturaSensor(
        timestamp=datetime.now(),
        punto_muestreo='entrada',
        biofiltro_id=None, # La entrada no pertenece a un biofiltro específico
        od=od_entrada,
        ph=ph_entrada,
        conductividad=conductividad_entrada,
        solidos_solubles=int(conductividad_entrada * 0.65), # Estimación
        turbidez=turbidez_entrada,
        volumen_agua=random.randint(80, 150),
        numero_usuarios=numero_usuarios,
        temperatura_agua=temperatura_agua,
        computed_eficiencia=False # Siempre se crea como no procesada
    )
    
    logger.debug(f"Lectura de ENTRADA simulada: Turbidez={turbidez_entrada}, OD={od_entrada}")

    # --- 2. Simular el efecto de "limpieza" de los 3 biofiltros para la SALIDA ---
    lecturas_salida = []
    for i in range(1, 4): # Para biofiltros con id 1, 2, y 3
        # Cada biofiltro tiene una "personalidad" o eficiencia ligeramente diferente
        factor_reduccion_turbidez = random.uniform(0.10, 0.20) # Remueve entre el 80% y 90%
        factor_reduccion_conductividad = random.uniform(0.55, 0.70)
        factor_aumento_od = random.uniform(2.5, 3.5)
        
        # Ajustar pH hacia la neutralidad
        ph_salida = ph_entrada + random.uniform(0.3, 0.8)
        ph_salida = min(ph_salida, 8.5) # Asegurar que no exceda límites lógicos
        
        lectura_salida = LecturaSensor(
            timestamp=datetime.now(), # Mismo timestamp que la entrada para agruparlas
            punto_muestreo='salida_biofiltro',
            biofiltro_id=i,
            od=round(od_entrada + factor_aumento_od + random.uniform(-0.3, 0.3), 2),
            ph=round(ph_salida, 1),
            conductividad=int(conductividad_entrada * factor_reduccion_conductividad),
            solidos_solubles=int((conductividad_entrada * factor_reduccion_conductividad) * 0.65),
            turbidez=int(turbidez_entrada * factor_reduccion_turbidez),
            volumen_agua=int(lectura_entrada.volumen_agua * 0.95), # Pequeña pérdida
            numero_usuarios=numero_usuarios,
            temperatura_agua=round(temperatura_agua - random.uniform(0.5, 1.5), 1),
            computed_eficiencia=False
        )
        lecturas_salida.append(lectura_salida)
        logger.debug(f"Lectura de SALIDA simulada para Biofiltro {i}: Turbidez={lectura_salida.turbidez}, OD={lectura_salida.od}")

    # --- 3. Guardar todas las lecturas en la base de datos ---
    try:
        db.add(lectura_entrada)
        db.add_all(lecturas_salida)
        db.commit()
        logger.success("4 nuevas lecturas (1 entrada, 3 salidas) simuladas y guardadas en la BD.")
    except Exception as e:
        logger.error(f"Error al guardar lecturas simuladas en la BD: {e}")
        db.rollback()