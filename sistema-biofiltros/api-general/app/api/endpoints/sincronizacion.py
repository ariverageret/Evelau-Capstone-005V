from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.thingSpeak_service import thingSpeak_service

router = APIRouter(prefix="/sincronizacion", tags=["Sincronización"])

@router.post("/thingspeak")
def sincronizar_thingspeak_manual(db: Session = Depends(get_db)):
    """
    Sincronización manual de datos desde ThingSpeak
    Útil para testing y para forzar una sincronización inmediata
    """
    try:
        registros = thingSpeak_service.sincronizar_datos(db)
        return {
            "message": "Sincronización manual completada",
            "registros_nuevos": registros
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en sincronización: {str(e)}"
        )

@router.get("/status")
def obtener_estado_sincronizacion():
    """Obtiene el estado actual del servicio de sincronización"""
    return {
        "scheduler_activo": scheduler.is_running,
        "intervalo_minutos": scheduler.interval / 60,
        "ultima_sincronizacion": "2024-01-01T00:00:00Z"  
    }