from fastapi import APIRouter
from app.api.endpoints import sensores, eficiencia

# Instancia principal del enrutador que servirá como punto de unión de todos los endpoints
api_router = APIRouter()

api_router.include_router(sensores.router, prefix="/lecturas-sensores", tags=["sensores"])
#api_router.include_router(eficiencia.router, prefix="/eficiencia", tags=["eficiencia"])
