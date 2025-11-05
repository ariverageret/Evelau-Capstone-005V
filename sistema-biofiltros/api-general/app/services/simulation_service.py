import random
from datetime import datetime
from sqlalchemy.orm import Session
from loguru import logger

from app.models.sensor import LecturaSensor 

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
    sst_entrada = random.randint(150, 350) + (numero_usuarios * 20) 
    
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
        sst=sst_entrada,
        turbidez=turbidez_entrada,
        volumen_agua=random.randint(80, 150),
        numero_usuarios=numero_usuarios,
        temperatura_agua=temperatura_agua,
        computed_eficiencia=False # Siempre se crea como no procesada
    )
    
    logger.debug(f"ENTRADA simulada: Turbidez={turbidez_entrada}, SST={sst_entrada}")

    # --- 2. Simular el efecto de "limpieza" de los 3 biofiltros para la SALIDA ---
    lecturas_salida = []
    
    # Definir los factores de reducción una sola vez para este ciclo
    factor_reduccion_turbidez = random.uniform(0.05, 0.20) # Remueve entre el 80% y 95%
    factor_reduccion_conductividad = random.uniform(0.55, 0.70)
    
    # --- Factor de reducción específico para SST ---
    # El biofiltro debería tener una alta tasa de remoción de sólidos.
    factor_reduccion_sst = random.uniform(0.05, 0.15) # Remueve entre el 85% y 95% 
    
    factor_aumento_od = random.uniform(2.5, 3.5)
    
    # Lógica secuencial para la simulación
    valor_actual = {
        'turbidez': turbidez_entrada,
        'sst': sst_entrada
    }

    for i in range(1, 4): # Para biofiltros con id 1, 2, y 3
        
        # Simulación de la salida de la etapa actual
        turbidez_salida = int(valor_actual['turbidez'] * factor_reduccion_turbidez * random.uniform(0.9, 1.1))
        sst_salida = int(valor_actual['sst'] * factor_reduccion_sst * random.uniform(0.9, 1.1))
        
        # Ajustar pH hacia la neutralidad
        ph_salida = ph_entrada + (i * random.uniform(0.2, 0.4)) # El pH sube un poco en cada etapa
        ph_salida = min(ph_salida, 8.5)
        
        lectura_salida = LecturaSensor(
            timestamp=datetime.now(),
            punto_muestreo='salida_biofiltro',
            biofiltro_id=i,
            od=round(od_entrada + (i * factor_aumento_od / 2.5) + random.uniform(-0.3, 0.3), 2),
            ph=round(ph_salida, 1),
            conductividad=int(conductividad_entrada * (factor_reduccion_conductividad + (i*0.05))), # Mejora un poco en cada etapa
            sst=max(5, sst_salida), # Asegura un mínimo
            turbidez=max(2, turbidez_salida), # Asegura un mínimo
            volumen_agua=int(lectura_entrada.volumen_agua * (1 - (i*0.02))),
            numero_usuarios=numero_usuarios,
            temperatura_agua=round(temperatura_agua - (i*0.5), 1),
            computed_eficiencia=False
        )
        lecturas_salida.append(lectura_salida)
        logger.debug(f"SALIDA simulada (Etapa {i}): Turbidez={lectura_salida.turbidez}, SST={lectura_salida.sst}")
        
        # La salida de esta etapa es la entrada de la siguiente
        valor_actual['turbidez'] = lectura_salida.turbidez
        valor_actual['sst'] = lectura_salida.sst

    # --- 3. Guardar todas las lecturas en la base de datos ---
    try:
        db.add(lectura_entrada)
        db.add_all(lecturas_salida)
        db.commit()
        logger.success("4 nuevas lecturas (1 entrada, 3 salidas) simuladas y guardadas en la BD.")
    except Exception as e:
        logger.error(f"Error al guardar lecturas simuladas en la BD: {e}")
        db.rollback()