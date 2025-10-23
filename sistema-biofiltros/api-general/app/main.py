from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.api_v1 import api_router
from app.utils.logging import configure_logging
from datetime import datetime
import pytz

from loguru import logger
from app.services.scheduler import start_scheduler, scheduler
from app.services.prediction_service import prediction_service 

#from app.core.database import Base, engine # Descomentar si usamos creación de tablas al inicio

# Configurar logging
configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código que se ejecuta al iniciar la aplicación
    logger.info("Iniciando aplicación...")

    # Verificar si el modelo de predicción se cargó correctamente al inicio
    if prediction_service.pipeline is None:
        logger.warning("El modelo de predicción NO se cargó correctamente al inicio.")
    else:
        logger.info("Modelo de predicción cargado y listo.")

    start_scheduler()
    
    yield
    
    # Código que se ejecuta al apagar la aplicación
    logger.info("Deteniendo aplicación...")
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler detenido.")
    else:
        logger.info("Scheduler no estaba corriendo.")

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

#@app.on_event("startup")
#def startup_event():
#    # Inicia el scheduler cuando la aplicación FastAPI arranca
#    start_scheduler()

# Incluir routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get('/', tags=['inicio'])
async def root():
    return HTMLResponse(
        f"""
                <h2>Sistema de Biofiltros API</h2>
                <p><strong>Versión:</strong> {settings.PROJECT_VERSION}</p>
                <p><strong>Mensaje:</strong> Sistema de Biofiltros API funcionando correctamente</p>
        """
    )

# Endpoint para verificar el estado del servidor
@app.get("/health", tags=['health'])
async def health_check():
    chile_tz = pytz.timezone("America/Santiago")
    timestamp = datetime.now(chile_tz).isoformat()
    return {
        "status": "healthy",
        "timestamp": timestamp
    }

# Endpoint para obtener información del sistema
@app.get("/info", tags=["info"])
async def info():
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "description": app.description
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",                      # Escucha en todas las interfaces de red
        port=8001,                          # Puerto donde se expone la API
        log_level="debug"     
    )
