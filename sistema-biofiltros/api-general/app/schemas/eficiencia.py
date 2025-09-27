from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal

class EficienciaBase(BaseModel):
    timestamp: datetime
    eficiencia_od_global: Optional[Decimal] = None
    eficiencia_turbidez_global: Optional[Decimal] = None
    eficiencia_bf1_turbidez: Optional[Decimal] = None
    eficiencia_bf2_turbidez: Optional[Decimal] = None
    eficiencia_bf3_turbidez: Optional[Decimal] = None
    cumple_norma: Optional[bool] = None

# --- Esquema para Creación ---
# Hereda de EficienciaBase. Se usará internamente para crear registros.
class EficienciaCreate(EficienciaBase):
    pass

# --- Esquema para Respuestas de API ---
# Hereda de EficienciaBase y añade el 'id'.
# Se usa para devolver datos desde la API al cliente.
class EficienciaResponse(EficienciaBase):
    id: int

    class Config:
        from_attributes = True
        # orm_mode = True