"""
Objetivo: definir modelo ORM `LecturaSensor` para almacenar lecturas de sensores en la BD usando SQLAlchemy.
"""

from sqlalchemy import Column, Integer, DateTime, Enum, Boolean, ForeignKey, Numeric
#from sqlalchemy import Numeric
from sqlalchemy.dialects.mysql import TINYINT
from app.core.database import Base

class LecturaSensor(Base):
    __tablename__ = "lecturas_sensores"                 
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, index=True, nullable=False)
    punto_muestreo = Column(Enum('entrada', 'salida_1', 'salida_2', 'salida_final'), index=True, nullable=False)
    biofiltro_id = Column(Integer, ForeignKey('biofiltros.id'), nullable=True)
    od = Column(Numeric(4, 2), nullable=True)
    ph = Column(Numeric(3, 1), nullable=True)
    conductividad = Column(Integer, nullable=True)
    solidos_solubles = Column(Integer, nullable=True)
    turbidez = Column(Integer, nullable=True)
    volumen_agua = Column(Integer, nullable=True)
    numero_usuarios = Column(TINYINT, nullable=True)
    temperatura_agua = Column(Numeric(3, 1), nullable=True)
    computed_eficiencia = Column(Boolean, default=False)