import requests
import logging
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any
from app.core.config import settings
from app.models.sensor import LecturaSensor
from app.schemas.sensor import LecturaSensorCreate

logger = logging.getLogger(__name__)

class ThingSpeakService:
    def __init__(self):
        self.base_url = "https://api.thingspeak.com"
        self.api_key = settings.THINGSPEAK_API_KEY
        self.channel_id = settings.THINGSPEAK_CHANNEL_ID
        
        # Mapeo: field_id de ThingSpeak -> columna en tu tabla
        self.field_mapping = {
            'field1': 'ph',
            'field2': 'conductividad', 
            'field3': 'turbidez',
            'field4': 'solidos_solubles',
            'field5': 'od',
            'field6': 'temperatura_agua'
        }
        
        # Mapeo: channel_id de ThingSpeak -> punto_muestreo y biofiltro_id
        self.channel_mapping = {
            'channel_entrada': {'punto_muestreo': 'entrada', 'biofiltro_id': None},
            'channel_salida_1': {'punto_muestreo': 'salida_1', 'biofiltro_id': 1},
            'channel_salida_2': {'punto_muestreo': 'salida_2', 'biofiltro_id': 2},
            'channel_salida_final': {'punto_muestreo': 'salida_final', 'biofiltro_id': 3}
        }

    def obtener_datos_thingspeak(self, channel_config: str, results: int = 10) -> List[Dict]:
        """Obtiene datos de un canal específico de ThingSpeak"""
        try:
            channel_info = self.channel_mapping[channel_config]
            url = f"{self.base_url}/channels/{self.channel_id}/feeds.json"
            
            params = {
                'api_key': self.api_key,
                'results': results
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            datos = response.json()
            feeds = datos.get('feeds', [])
            
            datos_procesados = []
            for feed in feeds:
                dato = {
                    'timestamp': datetime.strptime(feed['created_at'], '%Y-%m-%dT%H:%M:%SZ'),
                    'punto_muestreo': channel_info['punto_muestreo'],
                    'biofiltro_id': channel_info['biofiltro_id'],
                    'computed_eficiencia': False
                }
                
                # Mapear fields de ThingSpeak a columnas de la BD
                for field_name, column_name in self.field_mapping.items():
                    if field_name in feed and feed[field_name] is not None:
                        dato[column_name] = float(feed[field_name])
                
                datos_procesados.append(dato)
            
            logger.info(f"Obtenidos {len(datos_procesados)} registros de {channel_config}")
            return datos_procesados
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error conectando a ThingSpeak ({channel_config}): {e}")
            return []
        except Exception as e:
            logger.error(f"Error procesando datos de ThingSpeak ({channel_config}): {e}")
            return []

    def guardar_datos_en_db(self, db: Session, datos: List[Dict]):
        """Guarda los datos obtenidos en la base de datos"""
        try:
            registros_guardados = 0
            for dato in datos:
                # Verificar si el registro ya existe (evitar duplicados)
                existe = db.query(LecturaSensor).filter(
                    LecturaSensor.timestamp == dato['timestamp'],
                    LecturaSensor.punto_muestreo == dato['punto_muestreo']
                ).first()
                
                if not existe:
                    lectura = LecturaSensorCreate(**dato)
                    db_lectura = LecturaSensor(**lectura.dict())
                    db.add(db_lectura)
                    registros_guardados += 1
            
            db.commit()
            logger.info(f"Guardados {registros_guardados} nuevos registros en BD")
            return registros_guardados
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error guardando datos en BD: {e}")
            return 0

    def sincronizar_datos(self, db: Session):
        """Sincroniza datos de todos los canales de ThingSpeak"""
        total_registros = 0
        
        for channel_config in self.channel_mapping.keys():
            datos = self.obtener_datos_thingspeak(channel_config)
            if datos:
                registros_guardados = self.guardar_datos_en_db(db, datos)
                total_registros += registros_guardados
        
        return total_registros

# Instancia global del servicio
thingSpeak_service = ThingSpeakService()