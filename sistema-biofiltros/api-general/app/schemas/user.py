from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum


class EstadoUsuario(str, Enum):
    Activo = "Activo"
    Inactivo = "Inactivo"
    Bloqueado = "Bloqueado"

class UsuarioBase(BaseModel):
    username: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    username: str
    password_hash: str
    email: EmailStr
    rol: str
    estado: EstadoUsuario = EstadoUsuario.Activo


class UsuarioUpdate(BaseModel):
    id_usuario: int
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password_hash: Optional[str] = None
    estado: Optional[EstadoUsuario] = None
    rol: Optional[str] = None

class UsuarioResponse(UsuarioBase):
    id_usuario: int
    estado: EstadoUsuario
    fecha_creacion: datetime    
    rol : str

    class Config:
        from_attributes = True