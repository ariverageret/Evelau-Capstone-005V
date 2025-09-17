from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime
import pytz

# Crear aplicación FastAPI
app = FastAPI(
    title='Sistema Biofiltros',
    description='Proyecto CAPSTONE Prodesal Isla Maipo',
    version='0.0.1'
)

@app.get('/', tags=['inicio'])
async def root():
    return HTMLResponse(
        f"""
                <h2>Sistema de Biofiltros API</h2>
                <p><strong>Versión:</strong> {app.version}</p>
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
        "project_name": app.title,
        "version": app.version,
        "description": app.description
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",       # Escucha en todas las interfaces de red
        port=8000,            # Puerto donde se expone la API
        log_level="debug"     # Muestra más detalles en consola
    )
