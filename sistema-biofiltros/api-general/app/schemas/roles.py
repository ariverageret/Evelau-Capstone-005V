from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum

class TipoRol(str, Enum):
    Admin = "Admin"
    Agricultor = "Agricultor"
    Analista = "Analista"

class RolBase(BaseModel):
    nombre_rol: TipoRol
    descripcion: Optional[str] = None

class RolCreate(RolBase):
    nombre_rol: str
    descripcion: str = None

class RolResponse(RolBase):
    id_rol: int

    class Config:
        from_attributes = True

class RolUpdate(BaseModel):
    id_rol: int
    nombre_rol: Optional[str] = None
    descripcion: Optional[str] = None

class RoldeleteResponse(RolBase):
    id_rol: int

    class Config:
        from_attributes = True