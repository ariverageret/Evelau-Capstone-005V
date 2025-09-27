from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.models.roles import Rol, TipoRol
from app.schemas.roles import RolResponse, RolCreate, RolUpdate, RoldeleteResponse


# ---------------------- ROUTER ----------------------
router = APIRouter(tags=["roles"])
#---------------------- ENDPOINTS ----------------------

@router.post("/addRol", response_model=RolResponse)
def add_rol(rol: RolCreate, db: Session = Depends(get_db)):
    # Normalizar nombre del rol
    nombre_rol = rol.nombre_rol.strip()

    # Verificar si el rol ya existe
    existing_rol = db.query(Rol).filter(Rol.nombre_rol == nombre_rol).first()
    if existing_rol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rol ya existe."
        )
    
    # Crear nuevo rol
    new_rol = Rol(**rol.dict())
    db.add(new_rol)
    db.commit()
    db.refresh(new_rol)
    
    return new_rol

@router.post("/ModificarRol", response_model=RolResponse)
def modificar_rol(rol: RolUpdate, db: Session = Depends(get_db)):
    # Verificar si el rol existe
    existing_rol = db.query(Rol).filter(Rol.id_rol == rol.id_rol).first()
    if not existing_rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado."
        )
    
    # Actualizar solo si vienen valores nuevos
    if rol.nombre_rol:
        existing_rol.nombre_rol = rol.nombre_rol.strip()
    if rol.descripcion is not None:
        existing_rol.descripcion = rol.descripcion

    db.commit()
    db.refresh(existing_rol)
    
    return existing_rol

@router.get("/GetRoles", response_model=list[RolResponse])
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(Rol).all()
    return roles

@router.get("/GetRol/{rol_id}", response_model=RolResponse)
def get_rol(rol_id: int, db: Session = Depends(get_db)):
    rol = db.query(Rol).filter(Rol.id_rol == rol_id).first()
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado."
        )
    return rol

# @router.delete("/EliminarRol", response_model=RolResponse)
# def eliminar_rol(rol: RoldeleteResponse, db: Session = Depends(get_db)):
#     # Verificar si el rol existe
#     existing_rol = db.query(Rol).filter(Rol.id_rol == rol.id_rol).first()
#     if not existing_rol:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Rol no encontrado."
#         )
    
#     db.delete(existing_rol)
#     db.commit()
    
#     return existing_rol