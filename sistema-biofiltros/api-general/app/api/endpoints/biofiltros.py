from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.biofiltro import Biofiltro
from app.schemas.biofiltro import BiofiltroCreate, BiofiltroResponse

# ---------------------- CREAR ROUTER ----------------------
router = APIRouter()

# ---------------------- ENDPOINTS ----------------------
# ----------------------- Obtener Biofiltro existente
@router.get("/biofiltros", response_model=List[BiofiltroResponse])
def obtener_biofiltros(
    skip: int = 0,                          # número de registros a saltar (paginación)
    limit: int = 100,                       # límite máximo de registros a devolver
    db: Session = Depends(get_db)           # inyecta la sesión de base de datos en endpoint.
):
    # Obtener todos los biofiltros con paginación
    lecturas = db.query(Biofiltro).offset(skip).limit(limit).all()
    return lecturas

# ----------------------- Actualizar un biofiltro existente
@router.put("/biofiltros/{lectura_id}", response_model=BiofiltroResponse)
def actualizar_biofiltro(biofiltro_id: int, biofiltro: BiofiltroResponse, db: Session = Depends(get_db)):
    db_biofiltro = db.query(Biofiltro).filter(Biofiltro.id == biofiltro_id).first()
    if not db_biofiltro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lectura con ID {biofiltro_id} no encontrada"
        )
    
    # Actualizar cada campo con los valores del esquema recibido
    for key, value in biofiltro.dict().items():
        setattr(db_biofiltro, key, value)
    
    db.commit()                                                # guardar cambios en DB
    db.refresh(db_biofiltro)                                     # refrescar objeto actualizado
    return db_biofiltro
