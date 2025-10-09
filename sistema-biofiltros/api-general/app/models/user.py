"""
Objetivo: Definidir modelo ORM `User` para almacenar información de usuarios en la BD usando SQLAlchemy.
"""

from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class EstadoUsuario(enum.Enum):
    Activo = "Activo"
    Inactivo = "Inactivo"
    Bloqueado = "Bloqueado"

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(64), nullable=False) # Almacena el hash de la contraseña
    email = Column(String(100), unique=True, nullable=False)
    estado = Column(Enum(EstadoUsuario), default=EstadoUsuario.Activo, nullable=False)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    rol = Column(String(50), nullable=False, default="Agricultor")  # Nuevo campo para el rol del usuario