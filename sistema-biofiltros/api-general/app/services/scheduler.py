from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger
from app.core.database import SessionLocal
from app.core.config import settings
from app.services.simulation_service import generar_lecturas_simuladas 

# Importar la función que realiza el trabajo
from app.services.calculation_service import procesar_y_almacenar_eficiencia

scheduler = BackgroundScheduler(daemon=True)

def job_simular_lecturas():
    """Función de trabajo que llama al servicio de simulación."""
    logger.debug("Scheduler: Creando sesión de BD para el job de simulación.")
    db = SessionLocal()
    try:
        generar_lecturas_simuladas(db)
    finally:
        db.close()
        logger.debug("Scheduler: Sesión de BD de simulación cerrada.")


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
    Inicia el scheduler y añade todos los trabajos.
    """
    # Job de simulación: se ejecuta en el minuto 0 de cada hora
    #scheduler.add_job(job_simular_lecturas, 'cron', hour='*', minute='0') # Oficial

    scheduler.add_job(job_simular_lecturas, 'cron', minute='*/45') # Test
    
    # Job de cálculo: se ejecuta 15 minutos después
    intervalo = settings.SCHEDULER_INTERVAL_MINUTES
    #scheduler.add_job(job_calcular_eficiencia, 'cron', minute=f'*/{intervalo}') # Oficial
    scheduler.add_job(job_calcular_eficiencia, 'cron', minute='*/45') # Test
    
    try:
        scheduler.start()
        logger.info(f"Scheduler iniciado. Simulación a los :00. Cálculo cada {intervalo} min.")
    except Exception as e:
        logger.error(f"No se pudo iniciar el scheduler: {e}")