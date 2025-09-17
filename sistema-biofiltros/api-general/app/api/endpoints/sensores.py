from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.sensor import LecturaSensor
from app.schemas.sensor import LecturaSensorCreate, LecturaSensorResponse

# ---------------------- CREAR ROUTER ----------------------
router = APIRouter()

# ---------------------- ENDPOINTS ----------------------
@router.get("/lecturas-sensores", response_model=List[LecturaSensorResponse])
def obtener_lecturas_sensores(
    skip: int = 0,                          # número de registros a saltar (paginación)
    limit: int = 100,                       # límite máximo de registros a devolver
    db: Session = Depends(get_db)           # inyecta la sesión de base de datos en endpoint.
):
    # Obtener todas las lecturas de sensores con paginación
    lecturas = db.query(LecturaSensor).offset(skip).limit(limit).all()
    return lecturas

# ----------------------- Obtener una lectura específica por ID
@router.get("/lecturas-sensores/{lectura_id}", response_model=LecturaSensorResponse)
def obtener_lectura_sensor(lectura_id: int, db: Session = Depends(get_db)):
    lectura = db.query(LecturaSensor).filter(LecturaSensor.id == lectura_id).first()
    if not lectura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lectura con ID {lectura_id} no encontrada"
        )
    return lectura

# ----------------------- Crear una nueva lectura de sensor
@router.post("/lecturas-sensores", response_model=LecturaSensorResponse, status_code=status.HTTP_201_CREATED)
def crear_lectura_sensor(lectura: LecturaSensorCreate, db: Session = Depends(get_db)):
    db_lectura = LecturaSensor(**lectura.dict())                # convertir Pydantic a modelo ORM
    db.add(db_lectura)                                          # agregar a sesión
    db.commit()                                                 # guardar cambios en DB
    db.refresh(db_lectura)                                      # refrescar objeto con datos de DB
    return db_lectura

# ----------------------- Actualizar una lectura existente"""
@router.put("/lecturas-sensores/{lectura_id}", response_model=LecturaSensorResponse)
def actualizar_lectura_sensor(lectura_id: int, lectura: LecturaSensorCreate, db: Session = Depends(get_db)):
    db_lectura = db.query(LecturaSensor).filter(LecturaSensor.id == lectura_id).first()
    if not db_lectura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lectura con ID {lectura_id} no encontrada"
        )
    
    # Actualizar cada campo con los valores del esquema recibido
    for key, value in lectura.dict().items():
        setattr(db_lectura, key, value)
    
    db.commit()                                                # guardar cambios en DB
    db.refresh(db_lectura)                                     # refrescar objeto actualizado
    return db_lectura

# ----------------------- Eliminar una lectura de sensor
@router.delete("/lecturas-sensores/{lectura_id}")
def eliminar_lectura_sensor(lectura_id: int, db: Session = Depends(get_db)):
    db_lectura = db.query(LecturaSensor).filter(LecturaSensor.id == lectura_id).first()
    if not db_lectura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lectura con ID {lectura_id} no encontrada"
        )
    
    db.delete(db_lectura)                                       # eliminar de DB
    db.commit()                                                 # confirmar cambios
    return {"message": f"Lectura con ID {lectura_id} eliminada correctamente"}