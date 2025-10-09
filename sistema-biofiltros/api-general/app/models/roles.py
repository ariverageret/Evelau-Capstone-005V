"""
Objetivo: Definidir modelo ORM `Roles` para almacenar información de roles en la BD usando SQLAlchemy.
"""

from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class TipoRol(enum.Enum):
    Admin = "Admin"
    Agricultor = "Agricultor"
    Analista = "Analista"

class Rol(Base):
    __tablename__ = "rol"

    id_rol = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre_rol = Column(Enum(TipoRol), unique=True, nullable=False)
    descripcion = Column(String(255), nullable=True)