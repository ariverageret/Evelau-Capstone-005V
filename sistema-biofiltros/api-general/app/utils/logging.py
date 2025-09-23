"""
Objetivo: configurar logging centralizado usando loguru y capturar logs de librerías externas que usan el módulo estándar `logging`.
"""

import logging
import sys
from loguru import logger

# 'InterceptHandler' asegura que todos los logs pasen por Loguru, incluso los que no se generen directamente con él.
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Obtener nivel de log correspondiente en Loguru si existe
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno              # si no existe, usar nivel numérico
        
        # Encontrar el frame de quien originó el mensaje para mostrar el stack correcto
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        
        # Loggear el mensaje usando Loguru, incluyendo excepciones si las hay
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


"""
Función para configurar logging global del proyecto:
- Intercepta logs de cualquier librería que use `logging` estándar, los redirige a Loguru
- Configura Loguru para imprimir en stdout
"""
def configure_logging():
    # Interceptar todo desde el logger raíz
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.INFO)
    
    # Limpiar handlers de todos los loggers existentes y propagar a root
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
    
    # Configurar Loguru para imprimir en consola (stdout) | serialize=False indica que no queremos JSON, solo texto plano
    logger.configure(handlers=[{"sink": sys.stdout, "serialize": False}])


# ---------------------- NOTAS ----------------------
# - Esto unifica el logging de FastAPI, SQLAlchemy, Uvicorn y cualquier librería externa.
# - Usando Loguru se obtiene salida más clara, con colores y manejo de excepciones más sencillo.