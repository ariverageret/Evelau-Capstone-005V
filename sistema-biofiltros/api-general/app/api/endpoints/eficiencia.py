# C:\Users\mauro\Desktop\capstone\Evelau-Capstone-005V\sistema-biofiltros\api-general\app\api\endpoints\eficiencia.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

# Importar la dependencia de BD y los modelos/esquemas correctos
from app.core.database import get_db
from app.models.eficiencia import EficienciaInstantanea
from app.schemas.eficiencia import EficienciaResponse # Usamos el schema de respuesta

router = APIRouter()

@router.get("/", response_model=List[EficienciaResponse])
def obtener_registros_de_eficiencia(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene una lista de los registros de eficiencia calculados,
    ordenados por el más reciente primero. Ideal para dashboards.
    """
    eficiencias = db.query(EficienciaInstantanea).order_by(
        EficienciaInstantanea.timestamp.desc()
    ).offset(skip).limit(limit).all()
    return eficiencias

# La creación de registros de eficiencia es un proceso interno y automáticomanejado por el scheduler