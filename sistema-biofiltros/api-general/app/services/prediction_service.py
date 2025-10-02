import joblib
import pandas as pd
from pathlib import Path
from pydantic import BaseModel
from typing import Optional


# Esquema Pydantic para los datos de entrada de la predicción
class PredictionInput(BaseModel):
    ph_entrada: float
    conductividad_entrada: int
    turbidez_entrada: int
    od_entrada: float
    numero_usuarios: int
    temperatura_agua: float

class PredictionService:
    def __init__(self):
        # Se cargarán en la primera llamada a predict_compliance
        self.scaler: Optional[object] = None
        self.model: Optional[object] = None
        self.models_path = Path("app/ml_models")

    def _load_models(self):
        """Método privado para cargar los modelos si aún no están en memoria."""
        if self.model is None or self.scaler is None:
            # Crea el directorio si no existe para evitar errores en el futuro
            self.models_path.mkdir(parents=True, exist_ok=True)
            
            scaler_path = self.models_path / "compliance_scaler.joblib"
            model_path = self.models_path / "compliance_classifier.joblib"
            
            # Solo intenta cargar si los archivos existen
            if not scaler_path.exists() or not model_path.exists():
                raise FileNotFoundError("Los archivos del modelo de ML no se encuentran. Entrene el modelo primero.")
            
            self.scaler = joblib.load(scaler_path)
            self.model = joblib.load(model_path)

    def predict_compliance(self, input_data: PredictionInput) -> dict:
        """
        Realiza una predicción de cumplimiento normativo.
        """
        # Carga los modelos solo la primera vez que se llama a esta función
        try:
            self._load_models()
        except FileNotFoundError as e:
            # Si los archivos no existen, devuelve un error claro en la API en lugar de crashear la app
            return {"error": str(e)}

        df = pd.DataFrame([input_data.dict()])
        scaled_features = self.scaler.transform(df)
        prediction = self.model.predict(scaled_features)
        probability = self.model.predict_proba(scaled_features)
        
        cumple_norma = bool(prediction[0])
        confianza = probability[0][1] if cumple_norma else probability[0][0]
        
        return {
            "prediccion_cumple_norma": cumple_norma,
            "confianza": round(confianza, 4)
        }

# La instancia se crea, pero no carga nada pesado al inicio
prediction_service = PredictionService()