"""
Objetivo: definir modelo ORM `Biofiltro` para almacenar información de biofiltros en la BD usando SQLAlchemy.
"""

from sqlalchemy import Column, Integer, String, Date
from app.core.database import Base

class Biofiltro(Base):
    __tablename__ = "biofiltros"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_biofiltro = Column(String(50), nullable=False)
    especie_vegetal = Column(String(100), nullable=False)
    fecha_inicio = Column(Date, nullable=False)