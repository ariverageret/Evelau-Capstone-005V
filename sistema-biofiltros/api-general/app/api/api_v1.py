from fastapi import APIRouter
from app.api.endpoints import sensores, biofiltros

# Instancia principal del enrutador que servirá como punto de unión de todos los endpoints
api_router = APIRouter()

api_router.include_router(sensores.router, prefix="/lecturas-sensores", tags=["sensores"])
api_router.include_router(biofiltros.router, prefix="/biofiltro", tags=["biofiltros"])
