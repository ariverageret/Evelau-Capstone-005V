import time
import threading
import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.thingSpeak_service import thingSpeak_service

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self, interval_minutes: int = 15):
        self.interval = interval_minutes * 60  # Convertir a segundos
        self.is_running = False
        self.thread = None

    def tarea_sincronizacion(self):
        """Tarea que se ejecuta periódicamente para sincronizar datos"""
        while self.is_running:
            try:
                db = SessionLocal()
                try:
                    logger.info("Iniciando sincronización con ThingSpeak...")
                    registros = thingSpeak_service.sincronizar_datos(db)
                    logger.info(f"Sincronización completada. {registros} nuevos registros")
                finally:
                    db.close()
                
                # Esperar hasta la próxima ejecución
                time.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"Error en tarea de sincronización: {e}")
                time.sleep(60)  # Esperar 1 minuto antes de reintentar

    def iniciar(self):
        """Inicia el scheduler en un hilo separado"""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self.tarea_sincronizacion)
            self.thread.daemon = True  # Se cierra cuando la app principal se cierra
            self.thread.start()
            logger.info(f"Scheduler iniciado. Intervalo: {self.interval/60} minutos")

    def detener(self):
        """Detiene el scheduler"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        logger.info("Scheduler detenido")

# Instancia global del scheduler
scheduler = SchedulerService(interval_minutes=15)