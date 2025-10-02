from fastapi import APIRouter
from app.api.endpoints import sensores, biofiltros, auth, usuarios, roles, eficiencia, debug

# Instancia principal del enrutador que servirá como punto de unión de todos los endpoints
api_router = APIRouter()

api_router.include_router(sensores.router, prefix="/lecturas-sensores", tags=["sensores"])
api_router.include_router(biofiltros.router, prefix="/biofiltro", tags=["biofiltros"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"]) 
api_router.include_router(eficiencia.router, prefix="/eficiencia", tags=["eficiencia"]) 
#api_router.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
api_router.include_router(debug.router, prefix="/debug", tags=["Debug"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
