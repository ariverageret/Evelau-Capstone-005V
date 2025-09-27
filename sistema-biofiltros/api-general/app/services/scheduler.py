from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger
from app.core.database import SessionLocal
from app.core.config import settings

# Importar la función que realiza el trabajo
from app.services.calculation_service import procesar_y_almacenar_eficiencia

scheduler = BackgroundScheduler(daemon=True)

def job_calcular_eficiencia():
    """Función de trabajo que obtiene una sesión de BD y llama al servicio de cálculo."""
    logger.debug("Scheduler: Creando sesión de base de datos para el job.")
    db = SessionLocal()
    try:
        procesar_y_almacenar_eficiencia(db)
    except Exception as e:
        logger.error(f"Error durante la ejecución del job de cálculo de eficiencia: {e}")
    finally:
        db.close()
        logger.debug("Scheduler: Sesión de base de datos cerrada.")

def start_scheduler():
    """
    Inicia el scheduler y añade el trabajo de cálculo usando el intervalo de la configuración.
    """
    intervalo = settings.SCHEDULER_INTERVAL_MINUTES
    scheduler.add_job(job_calcular_eficiencia, 'cron', minute=f'*/{intervalo}')
    
    try:
        scheduler.start()
        logger.info(f"Scheduler iniciado. El cálculo de eficiencia se ejecutará cada {intervalo} minutos.")
    except Exception as e:
        logger.error(f"No se pudo iniciar el scheduler: {e}")

"""class SchedulerService:
    def __init__(self, interval_minutes: int = 15):
        self.interval = interval_minutes * 60  # Convertir a segundos
        self.is_running = False
        self.thread = None

    def tarea_sincronizacion(self):
        #Tarea que se ejecuta periódicamente para sincronizar datos
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
        #Inicia el scheduler en un hilo separado
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self.tarea_sincronizacion)
            self.thread.daemon = True  # Se cierra cuando la app principal se cierra
            self.thread.start()
            logger.info(f"Scheduler iniciado. Intervalo: {self.interval/60} minutos")

    def detener(self):
        #Detiene el scheduler
        self.is_running = False
        if self.thread:
            self.thread.join()
        logger.info("Scheduler detenido")

# Instancia global del scheduler
scheduler = SchedulerService(interval_minutes=15)"""