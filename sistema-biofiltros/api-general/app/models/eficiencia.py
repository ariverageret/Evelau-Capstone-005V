"""
Objetivo: definir modelo ORM `EficienciaInstantanea` para almacenar la eficiencia instantánea de los biofiltros y su cumplimiento de norma.
"""

from sqlalchemy import Column, Integer, DateTime, Enum, Boolean, ForeignKey, Numeric
from app.core.database import Base

class EficienciaInstantanea(Base):
    __tablename__ = "eficiencia_instantanea"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, index=True, nullable=False)
    eficiencia_od_global = Column(Numeric(5, 2), nullable=True)
    eficiencia_turbidez_global = Column(Numeric(5, 2), nullable=True)
    eficiencia_bf1_turbidez = Column(Numeric(5, 2), nullable=True)
    eficiencia_bf2_turbidez = Column(Numeric(5, 2), nullable=True)
    eficiencia_bf3_turbidez = Column(Numeric(5, 2), nullable=True)
    cumple_norma = Column(Boolean, nullable=True)