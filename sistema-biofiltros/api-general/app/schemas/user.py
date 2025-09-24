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
    password: str 

class UsuarioResponse(UsuarioBase):
    id_usuario: int
    estado: EstadoUsuario
    fecha_creacion: datetime

    class Config:
        from_attributes = True