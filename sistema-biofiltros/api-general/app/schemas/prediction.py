from pydantic import BaseModel, Field
from typing import List

# --- Esquema de Entrada ---
# IMPORTANTE: Los nombres de los campos DEBEN coincidir EXACTAMENTE
# con las columnas que se usaron para entrenar el modelo (guardadas en model_columns.joblib).

class PredictionInput(BaseModel):
    ph_entrada: float = Field(..., example=7.1, description="pH medido a la entrada del sistema.")
    conductividad_entrada: int = Field(..., example=1850, description="Conductividad eléctrica a la entrada (µS/cm).")
    turbidez_entrada: int = Field(..., example=150, description="Turbidez medida a la entrada (NTU).")
    od_entrada: float = Field(..., example=1.5, description="Oxígeno disuelto medido a la entrada (mg/L).")
    numero_usuarios: int = Field(..., example=4, description="Número de usuarios estimados en la vivienda.")
    temperatura_agua: float = Field(..., example=22.5, description="Temperatura del agua a la entrada (°C).")
    sst: int = Field(..., example=250, description="Sólidos suspendidos totales estimados/medidos a la entrada (mg/L).")
    volumen_agua_entrada: int = Field(..., example=120, description="Volumen estimado de agua gris entrante (Litros).")
    # Añadir aquí CUALQUIER OTRA FEATURE que incluyamos en el entrenamiento final

    class Config:
        json_schema_extra = {
            "example": {
                "ph_entrada": 7.1,
                "conductividad_entrada": 1850,
                "turbidez_entrada": 150,
                "od_entrada": 1.5,
                "numero_usuarios": 4,
                "temperatura_agua": 22.5,
                "sst": 250,
                "volumen_agua_entrada": 120
            }
        }

# --- Esquema de Salida ---
# Define la estructura de la respuesta que dará nuestra API.

class PredictionOutput(BaseModel):
    prediccion_cumple_norma: bool = Field(..., description="Predicción binaria: True si se espera que cumpla la norma, False si no.")
    probabilidad_cumplimiento: float = Field(..., example=0.85, description="Probabilidad estimada (entre 0 y 1) de que el agua cumpla la norma.")