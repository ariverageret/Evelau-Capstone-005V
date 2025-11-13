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
    sst: Optional[int] = None  
    
class LecturaSensorCreate(LecturaSensorBase):
    pass

class LecturaSensorResponse(LecturaSensorBase):
    id: int
    
    class Config:
        from_attributes = True