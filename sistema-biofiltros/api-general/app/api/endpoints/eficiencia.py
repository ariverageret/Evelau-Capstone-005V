"""from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.eficiencia import EficienciaInstantanea
#from app.schemas.eficiencia import EficienciaCreate, EficienciaResponse

# ---------------------- CREAR ROUTER ----------------------
router = APIRouter()

# ---------------------- ENDPOINTS ----------------------
# ----------------------- Obtener registros de eficiencia
@router.get("/eficiencia", response_model=List[EficienciaResponse])
def obtener_eficiencias(
    skip: int = 0,                          # número de registros a saltar (paginación)
    limit: int = 100,                       # límite máximo de registros a devolver
    db: Session = Depends(get_db)           # inyecta la sesión de base de datos en endpoint.
):
    # Obtener todos los registros de eficiencia con paginación
    eficiencias = db.query(EficienciaInstantanea).offset(skip).limit(limit).all()
    return eficiencias

# ----------------------- Crear un nuevo registro de eficiencia
@router.post("/eficiencia", response_model=EficienciaResponse)
def crear_eficiencia(eficiencia: EficienciaCreate, db: Session = Depends(get_db)):
    db_eficiencia = EficienciaInstantanea(**eficiencia.dict())          # convertir Pydantic a modelo ORM
    db.add(db_eficiencia)                                               # agregar a sesión
    db.commit()                                                         # guardar cambios en DB
    db.refresh(db_eficiencia)                                           # refrescar objeto con datos de DB
    return db_eficiencia"""