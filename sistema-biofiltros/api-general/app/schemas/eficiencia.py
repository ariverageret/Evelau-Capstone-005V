from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LecturaSensorBase(BaseModel):
    timestamp: datetime
    punto_muestreo: str
    biofiltro_id: Optional[int] = None
    od: Optional[float] = None
    ph: Optional[float] = None
    conductividad: Optional[int] = None
    solidos_solubles: Optional[int] = None
    turbidez: Optional[int] = None
    volumen_agua: Optional[int] = None
    numero_usuarios: Optional[int] = None
    temperatura_agua: Optional[float] = None
    computed_eficiencia: bool = False

class LecturaSensorCreate(LecturaSensorBase):
    pass

class LecturaSensorResponse(LecturaSensorBase):
    id: int
    
    class Config:
        orm_mode = True


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