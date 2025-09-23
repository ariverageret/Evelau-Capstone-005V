from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.api_v1 import api_router
from app.utils.logging import configure_logging 
from datetime import datetime
import pytz

# Importar logger de loguru directamente
from loguru import logger

# Importar los componentes necesarios para el lifespan
from app.services.scheduler import scheduler
from app.core.database import Base, engine

# Configurar logging
configure_logging()

"""@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Iniciar scheduler cuando la app comienza
    Base.metadata.create_all(bind=engine)  # Crear tablas si no existen
    scheduler.iniciar()
    logger.info("Aplicación y scheduler iniciados")
    
    yield
    
    # Shutdown: Detener scheduler cuando la app termina
    scheduler.detener()
    logger.info("Aplicación y scheduler detenidos")"""

# Endpoints básicos
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
    #lifespan=lifespan 
)

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
        port=8000,                          # Puerto donde se expone la API
        log_level="debug"     
    )
