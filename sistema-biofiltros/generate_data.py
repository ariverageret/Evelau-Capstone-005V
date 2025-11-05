import random
import datetime
from decimal import Decimal

# --- Parámetros de la Norma NCh 1333 (para referencia) ---
NORMA_PH_MIN = 6.5
NORMA_PH_MAX = 8.5
NORMA_CONDUCTIVIDAD_MAX = 2000
NORMA_TURBIDEZ_MAX = 5
NORMA_OD_MIN = 2
NORMA_SST_MAX = 30

# --- Función para Verificar Cumplimiento ---
def check_compliance(reading):
    if not (NORMA_PH_MIN <= reading['ph'] <= NORMA_PH_MAX): return False
    if reading['conductividad'] > NORMA_CONDUCTIVIDAD_MAX: return False
    if reading['turbidez'] > NORMA_TURBIDEZ_MAX: return False
    if reading['od'] < NORMA_OD_MIN: return False
    if reading['sst'] > NORMA_SST_MAX: return False
    return True

# --- Función para Calcular Eficiencia ---
def calculate_efficiency(val_in, val_out):
    if val_in is None or val_out is None or val_in == 0:
        return None
    eff = ((val_in - val_out) / val_in) * 100
    return round(Decimal(eff), 2)

# --- Generador Principal de Datos ---
def generate_realistic_cycle(target_compliance: bool, start_time: datetime):
    # (Esta función es la misma que ya teníamos, no necesita cambios)
    # ... (código interno de la función para generar los datos)
    # 1. Generar ENTRADA (Agua Sucia)
    num_users = random.randint(2, 6)
    temp_agua = round(random.uniform(18.0, 28.0), 1)
    entrada = {
        'timestamp': start_time.strftime('%Y-%m-%d %H:%M:%S'),
        'punto_muestreo': 'entrada',
        'biofiltro_id': 'NULL',
        'od': round(random.uniform(0.5, 2.0), 2),
        'ph': round(random.uniform(6.0, 7.8), 1),
        'conductividad': random.randint(1600, 2500) + num_users * 30,
        'sst': random.randint(180, 400) + num_users * 15,
        'turbidez': random.randint(150, 300) + num_users * 10,
        'volumen_agua': random.randint(70, 160),
        'numero_usuarios': num_users,
        'temperatura_agua': temp_agua,
        'computed_eficiencia': 0
    }

    # 2. Generar SALIDAS (Secuenciales con control)
    salidas = []
    current_reading = entrada.copy()
    eff_factor_turb = random.uniform(0.85, 0.98)
    eff_factor_sst = random.uniform(0.88, 0.97)
    od_increase_per_stage = random.uniform(1.0, 1.8)

    for i in range(1, 4):
        stage_reading = current_reading.copy()
        stage_reading['punto_muestreo'] = 'salida_biofiltro'
        stage_reading['biofiltro_id'] = i
        stage_reading['timestamp'] = (start_time + datetime.timedelta(minutes=i*2)).strftime('%Y-%m-%d %H:%M:%S')

        stage_reading['turbidez'] = max(2, int(current_reading['turbidez'] * (1 - eff_factor_turb * random.uniform(0.9, 1.1) / (i*0.8) )))
        stage_reading['sst'] = max(5, int(current_reading['sst'] * (1 - eff_factor_sst * random.uniform(0.9, 1.1) / (i*0.8) )))
        stage_reading['conductividad'] = max(300, int(current_reading['conductividad'] * random.uniform(0.85, 0.95)))
        stage_reading['od'] = round(current_reading['od'] + od_increase_per_stage * random.uniform(0.8, 1.2), 2)
        stage_reading['ph'] = round(min(NORMA_PH_MAX - 0.1, max(NORMA_PH_MIN + 0.1, current_reading['ph'] + random.uniform(0.1, 0.3))), 1)
        stage_reading['temperatura_agua'] = round(current_reading['temperatura_agua'] - random.uniform(0.2, 0.6), 1)

        if i == 3:
            final_compliance = check_compliance(stage_reading)
            if final_compliance != target_compliance:
                if target_compliance:
                    stage_reading['turbidez'] = max(2, stage_reading['turbidez'] - random.randint(1, NORMA_TURBIDEZ_MAX))
                    stage_reading['sst'] = max(5, stage_reading['sst'] - random.randint(1, NORMA_SST_MAX))
                    stage_reading['od'] = max(NORMA_OD_MIN + 0.1, stage_reading['od'] + random.uniform(0.1, 0.5))
                else:
                    param_to_fail = random.choice(['turbidez', 'sst', 'od'])
                    if param_to_fail == 'turbidez':
                        stage_reading['turbidez'] = NORMA_TURBIDEZ_MAX + random.randint(1, 5)
                    elif param_to_fail == 'sst':
                        stage_reading['sst'] = NORMA_SST_MAX + random.randint(1, 10)
                    else:
                        stage_reading['od'] = max(0, NORMA_OD_MIN - random.uniform(0.1, 0.5))

        salidas.append(stage_reading)
        current_reading = stage_reading

    bf1, bf2, bf3 = salidas[0], salidas[1], salidas[2]
    eff_turb_1 = calculate_efficiency(entrada['turbidez'], bf1['turbidez'])
    eff_turb_2 = calculate_efficiency(bf1['turbidez'], bf2['turbidez'])
    eff_turb_3 = calculate_efficiency(bf2['turbidez'], bf3['turbidez'])
    eff_turb_global = calculate_efficiency(entrada['turbidez'], bf3['turbidez'])
    eff_od_global = round(Decimal(bf3['od'] - entrada['od']), 2) if entrada['od'] is not None and bf3['od'] is not None else None

    cumple_norma_final = check_compliance(bf3)
    eficiencia_record = {
        'timestamp': (start_time + datetime.timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S'),
        'eficiencia_od_global': eff_od_global,
        'eficiencia_turbidez_global': eff_turb_global,
        'eficiencia_bf1_turbidez': eff_turb_1,
        'eficiencia_bf2_turbidez': eff_turb_2,
        'eficiencia_bf3_turbidez': eff_turb_3,
        'cumple_norma': 1 if cumple_norma_final else 0
    }
    return [entrada] + salidas, eficiencia_record


# --- NUEVO: Función principal que ejecuta todo el proceso ---
def main():
    """
    Función principal para generar los datos y crear el archivo SQL.
    """
    all_lecturas = []
    all_eficiencias = []
    current_time = datetime.datetime.now()

    print("Generando 1000 ciclos de datos (esto puede tardar un poco)...")
    targets = ([True] * 500) + ([False] * 500)
    random.shuffle(targets)

    for target in targets:
        lecturas, eficiencia = generate_realistic_cycle(target, current_time)
        all_lecturas.extend(lecturas)
        all_eficiencias.append(eficiencia)
        current_time += datetime.timedelta(hours=1)

    print(f"Generados {len(all_lecturas)} registros para lecturas_sensores.")
    print(f"Generados {len(all_eficiencias)} registros para eficiencia_instantanea.")

    # Para generar TODOS los INSERTs
    print("\nGenerando archivo SQL completo...")
    with open("generated_inserts.sql", "w", encoding="utf-8") as f:
        f.write("-- INSERTs para lecturas_sensores --\n")
        for lectura in all_lecturas:
            cols = ", ".join(lectura.keys())
            vals = list(lectura.values())
            formatted_vals = []
            for v in vals:
                if v == 'NULL':
                    formatted_vals.append('NULL')
                elif isinstance(v, str):
                    formatted_vals.append(f"'{v}'")
                else:
                    formatted_vals.append(str(v))
            f.write(f"INSERT INTO lecturas_sensores ({cols}) VALUES ({', '.join(formatted_vals)});\n")

        f.write("\n-- INSERTs para eficiencia_instantanea --\n")
        for eficiencia in all_eficiencias:
            cols_eff = ", ".join(eficiencia.keys())
            vals_eff = list(eficiencia.values())
            formatted_vals_eff = []
            for v in vals_eff:
                if v is None:
                     formatted_vals_eff.append('NULL')
                elif isinstance(v, str):
                    formatted_vals_eff.append(f"'{v}'")
                elif isinstance(v, Decimal):
                    formatted_vals_eff.append(str(v))
                else:
                    formatted_vals_eff.append(str(v))
            f.write(f"INSERT INTO eficiencia_instantanea ({cols_eff}) VALUES ({', '.join(formatted_vals_eff)});\n")

    print("✅ Archivo 'generated_inserts.sql' creado exitosamente en la misma carpeta.")


# --- NUEVO: El "botón de encendido" del script ---
# Este bloque de código le dice a Python que ejecute la función main()
# solo cuando el archivo se corre directamente.
if __name__ == "__main__":
    main()