from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.core.config import settings
from app.api.api_v1 import api_router
from app.utils.logging import configure_logging
from datetime import datetime
import pytz

# Configurar logging
configure_logging()

# Endpoints básicos
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
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
