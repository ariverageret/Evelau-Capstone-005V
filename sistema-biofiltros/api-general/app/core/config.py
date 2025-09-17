"""
Objetivo: definir configuración central del proyecto usando Pydantic BaseSettings,
permitiendo cargar valores desde variables de entorno o un archivo `.env`.
"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sistema de Biofiltros API"
    PROJECT_VERSION: str = "1.0.0"
    
    # ---------------------- CONFIGURACIÓN DE LA BASE DE DATOS ----------------------
    DATABASE_URL: str = "mysql+pymysql://user:password@localhost/biofiltros_db"             # Ejemplo
    
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
    
    # ---------------------- CONFIGURACIÓN DE ENVIRONMENTS ----------------------
    class Config:
        env_file = ".env"

# Crear una instancia global de configuración
settings = Settings()