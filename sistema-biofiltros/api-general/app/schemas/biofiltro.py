from pydantic import BaseModel
from datetime import date
from typing import Optional

class BiofiltroBase(BaseModel):
        nombre_biofiltro: str
        especie_vegetal: str
        fecha_inicio: date

class BiofiltroCreate(BiofiltroBase):
    pass

class BiofiltroResponse(BiofiltroBase):
    id: int
    
    class Config:
        from_attributes = True