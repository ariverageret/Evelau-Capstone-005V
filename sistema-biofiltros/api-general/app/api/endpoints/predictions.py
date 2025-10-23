from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.services.prediction_service import prediction_service
from app.schemas.prediction import PredictionInput, PredictionOutput

router = APIRouter()

@router.post(
    "/cumplimiento", # La ruta completa será /api/v1/predictions/cumplimiento
    response_model=PredictionOutput,
    summary="Predecir Cumplimiento Normativo del Agua Tratada",
    description="Recibe las características del agua de **entrada** y predice si el agua **tratada final** cumplirá con la norma NCh 1333.",
    tags=["Predictions"] # Etiqueta para agrupar en la documentación
)
async def predict_cumplimiento_normativo(
    input_data: PredictionInput # FastAPI valida automáticamente la entrada con este esquema
):
    """
    Realiza una predicción sobre el cumplimiento de la norma NCh 1333.

    - **input_data**: Objeto JSON con las características del agua de entrada.
    - **Returns**: Un objeto JSON con la predicción (True/False) y la probabilidad.
    """
    logger.info("Recibida solicitud de predicción de cumplimiento.")
    
    if prediction_service.pipeline is None:
        logger.error("Solicitud de predicción fallida: Modelo no cargado.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de predicción no está disponible (modelo no cargado)."
        )

    result = prediction_service.predict(input_data)

    if result is None:
        logger.error("Error interno durante la predicción.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error al procesar la predicción."
        )

    return result