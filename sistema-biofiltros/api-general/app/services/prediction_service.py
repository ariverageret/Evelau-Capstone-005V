import joblib
import pandas as pd
from pathlib import Path
from loguru import logger
from cachetools import cached, LRUCache, keys
import numpy as np
from app.schemas.prediction import PredictionInput, PredictionOutput

# --- Crear una función 'key' personalizada ---
# Esta función toma los argumentos de 'predict' y crea una tupla hashable
def custom_cache_key(func_self, input_data: PredictionInput):
    # Convertimos el Pydantic a dict, lo ordenamos por clave, y lo convertimos a tupla
    # Esto asegura que la misma entrada siempre genere la misma clave hashable
    return keys.hashkey(tuple(sorted(input_data.model_dump().items())))

class PredictionService:
    def __init__(self):
        self.pipeline = None
        self.model_columns = None
        self._load_model() 

    def _load_model(self):
        models_path = Path("app/ml_models")
        # IMPORTANTE: Asegurarse que los nombres coincidan con los archivos guardados
        pipeline_path = models_path / "final_model_pipeline.joblib"
        columns_path = models_path / "model_columns.joblib"
        try:
            logger.info(f"Cargando pipeline de modelo desde: {pipeline_path}")
            self.pipeline = joblib.load(pipeline_path)
            logger.info(f"Cargando columnas del modelo desde: {columns_path}")
            self.model_columns = joblib.load(columns_path)
            # --- OBTENER SOLO LAS COLUMNAS ORIGINALES ESPERADAS EN LA ENTRADA ---
            # Asumimos que las primeras 8 columnas en model_columns son las originales
            self.original_input_columns = self.model_columns[:8].tolist() # Ajustar el número si es diferente
            logger.success("Modelo y columnas cargados exitosamente.")
            logger.debug(f"Columnas ORIGINALES esperadas en la entrada: {self.original_input_columns}")
            logger.debug(f"Columnas TOTALES esperadas por el pipeline: {self.model_columns.tolist()}")
        except Exception as e:
            logger.error(f"Error al cargar artefactos del modelo: {e}")
            self.pipeline = None
            self.model_columns = None
            self.original_input_columns = None

    # --- Implementación de Caché ---
    # Usamos un caché LRU (Least Recently Used) con un tamaño máximo de 128 entradas.
    # Guarda los resultados de predicciones para entradas idénticas, evitando recalcular.
    @cached(cache=LRUCache(maxsize=128), key=custom_cache_key)
    def predict(self, input_data: PredictionInput) -> PredictionOutput | None:
        """
        Realiza una predicción usando el pipeline cargado.
        Aplica preprocesamiento (escalado) automáticamente gracias al pipeline.
        Retorna None si el modelo no está cargado.
        """
        if self.pipeline is None or self.model_columns is None or self.original_input_columns is None:
            logger.error("Intento de predicción fallido: El modelo o sus artefactos no están cargados.")
            return None

        try:
            # 1. Convertir entrada Pydantic a DataFrame de Pandas (SOLO con columnas originales)
            input_dict = input_data.model_dump()
            # Asegura que solo tomamos los campos que realmente vienen en la entrada
            input_df = pd.DataFrame([input_dict], columns=self.original_input_columns)

            # --- 2. APLICAR EXACTAMENTE EL MISMO FEATURE ENGINEERING DEL NOTEBOOK ---
            logger.debug("Aplicando Feature Engineering a los datos de entrada...")
            # Replicar CADA paso de la Celda 5.5 del notebook
            # Crear Features de Interacción
            input_df['turbidez_x_sst'] = input_df['turbidez_entrada'] * input_df['sst']
            input_df['ph_x_conductividad'] = input_df['ph_entrada'] * input_df['conductividad_entrada']
            # Crear Features Polinómicas
            input_df['turbidez_entrada_sq'] = input_df['turbidez_entrada']**2
            input_df['sst_sq'] = input_df['sst']**2
            # Crear Ratios (con manejo de división por cero)
            input_df['sst_div_turbidez'] = input_df['sst'] / (input_df['turbidez_entrada'] + 1e-6)
            input_df['conductividad_div_ph'] = input_df['conductividad_entrada'] / (input_df['ph_entrada'] + 1e-6)

            # --- 3. REORDENAR Y LIMPIAR ---
            # Asegurar que las columnas estén en el ORDEN EXACTO que espera el pipeline
            input_df = input_df[self.model_columns] # Reordena usando la lista guardada

            # Rellenar posibles infinitos o NaN (aunque no deberían ocurrir con +1e-6)
            input_df.replace([np.inf, -np.inf], np.nan, inplace=True)
            input_df.fillna(0, inplace=True) # Rellenar NaNs residuales con 0

            logger.debug(f"DataFrame TRAS Feature Engineering (listo para pipeline):\n{input_df}")
            if input_df.isnull().values.any():
                 logger.warning("¡Alerta! Aún hay NaNs antes de la predicción.")

            # --- 4. Realizar la predicción ---
            # El pipeline se encarga del escalado automáticamente.
            prediction = self.pipeline.predict(input_df)[0]
            probabilities = self.pipeline.predict_proba(input_df)[0]
            probability_cumplimiento = probabilities[1]

            logger.info(f"Predicción realizada: Cumple={bool(prediction)}, Probabilidad={probability_cumplimiento:.4f}")

            # --- 5. Formatear la salida ---
            return PredictionOutput(
                prediccion_cumple_norma=bool(prediction),
                probabilidad_cumplimiento=round(probability_cumplimiento, 4)
            )

        except Exception as e:
            logger.error(f"Error durante la predicción: {e}", exc_info=True) # exc_info=True da más detalle
            logger.error(f"Datos de entrada originales: {input_data.model_dump()}")
            # logger.error(f"DataFrame tras F.E.:\n{input_df.to_string()}") # Descomentar para debug extremo
            return None

prediction_service = PredictionService()