"""
Objetivo: definir configuración central del proyecto usando Pydantic BaseSettings,
permitiendo cargar valores desde variables de entorno o un archivo `.env`.
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sistema de Biofiltros API"
    PROJECT_VERSION: str = "1.0.0"
    
    # ---------------------- CONFIGURACIÓN DE LA BASE DE DATOS ----------------------
    #DATABASE_URL: str = "mysql+pymysql://user:password@localhost/biofiltros_db"             # Ejemplo
    DATABASE_URL: str = "mysql+pymysql://root:bio123@localhost/sistema_biofiltros"

    # ---------------------- CONFIGURACIÓN DE LA API ----------------------
    API_V1_STR: str = "/api/v1"
    
    # ---------------------- SEGURIDAD ----------------------
    SECRET_KEY: str = "your-secret-key-change-in-production"            # Ejemplo clave secreta para firmar JWT
    ALGORITHM: str = "HS256"                                            # Algoritmo de encriptación para tokens JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30                               # Tiempo de expiración de los tokens en minutos
    
    # ---------------------- CONFIGURACIÓN DE CORS ----------------------
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]            # Ej: frontend local o staging
    
    # ---------------------- CONFIGURACIÓN DE THINGSPEAK ----------------------
    
    THINGSPEAK_API_KEY: str = "your-thingspeak-api-key"                     # API Key para enviar datos a ThingSpeak 
    THINGSPEAK_CHANNEL_ID: str = "your-channel-id"                          # ID del canal de ThingSpeak donde se almacenan los datos
    
    THINGSPEAK_API_KEY: str = os.getenv("THINGSPEAK_API_KEY", "your-thingspeak-api-key")
    THINGSPEAK_CHANNEL_ID: str = os.getenv("THINGSPEAK_CHANNEL_ID", "your-channel-id")

    # ---------------------- CONFIGURACIÓN DE SCHEDULER ----------------------
    SCHEDULER_INTERVAL_MINUTES: int = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", 15))

    # ---------------------- UMBRALES NORMATIVOS (NCh 1333) ----------------------
    NORMA_PH_MIN: float = 6.5
    NORMA_PH_MAX: float = 8.5
    NORMA_CONDUCTIVIDAD_MAX: int = 2000
    NORMA_TURBIDEZ_MAX: int = 5
    NORMA_OD_MIN: int = 2
    NORMA_SST_MAX: int = 30  

    # ---------------------- CONFIGURACIÓN DE ENVIRONMENTS ----------------------
    class Config:
        env_file = ".env"

# Crear una instancia global de configuración
settings = Settings()