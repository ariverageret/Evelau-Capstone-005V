from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.simulation_service import generar_lecturas_simuladas

router = APIRouter()

@router.post(
    "/simulate-reading",
    status_code=status.HTTP_201_CREATED,
    summary="Generar un nuevo conjunto de lecturas de sensores"
)
def simulate_new_sensor_readings(db: Session = Depends(get_db)):
    """
    Endpoint de depuración para simular la llegada de nuevos datos de sensores.
    
    Crea 4 nuevos registros en la tabla `lecturas_sensores`:
    - 1 para el punto de muestreo 'entrada'.
    - 3 para el punto de muestreo 'salida_biofiltro' (uno por cada biofiltro).
    
    Estos datos pueden ser luego procesados por el job de cálculo de eficiencia.
    """
    try:
        generar_lecturas_simuladas(db)
        return {"message": "Datos de sensores simulados y guardados exitosamente."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al simular los datos: {str(e)}"
        )