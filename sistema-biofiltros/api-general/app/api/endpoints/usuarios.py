from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.models.user import Usuario, EstadoUsuario
from app.schemas.user import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.core.security import hash_password

# ---------------------- ROUTER ----------------------
router = APIRouter(tags=["usuarios"])

#---------------------- ENDPOINTS ----------------------
@router.post("/addUsuario", response_model=UsuarioResponse)
def add_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # Normalizar username y email
    username = usuario.username.strip().lower()
    email = usuario.email.strip().lower()

    # Verificar si el username o email ya existen
    existing_user = db.query(Usuario).filter(
        or_(Usuario.username == username, Usuario.email == email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario o correo electrónico ya están en uso."
        )
    # Hashear la contraseña antes de almacenarla
    usuario.password_hash = hash_password(usuario.password_hash)
    
    # Crear nuevo usuario
    new_user = Usuario(**usuario.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    
    return new_user

@router.post("/ModificarUsuario", response_model=UsuarioResponse)
def modificar_usuario(usuario: UsuarioUpdate, db: Session = Depends(get_db)):
    # Verificar si el usuario existe
    existing_user = db.query(Usuario).filter(Usuario.id_usuario == usuario.id_usuario).first()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    
    # Actualizar solo si vienen valores nuevos
    if usuario.username:
        existing_user.username = usuario.username.strip().lower()
    if usuario.email:
        existing_user.email = usuario.email.strip().lower()
    if usuario.password_hash:
        existing_user.password_hash = hash_password(usuario.password_hash)
    if usuario.estado:
        existing_user.estado = usuario.estado

    db.commit()
    db.refresh(existing_user)

    return existing_user


@router.get("/GetUsuarios", response_model=list[UsuarioResponse])
def get_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return usuarios

@router.get("/GetUsuario/{id_usuario}", response_model=UsuarioResponse)
def get_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    return usuario

@router.delete("/DeleteUsuario/{id_usuario}", response_model=UsuarioResponse)
def delete_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    
    usuario.estado = EstadoUsuario.Inactivo
    db.commit()
    db.refresh(usuario)
    
    return usuario
