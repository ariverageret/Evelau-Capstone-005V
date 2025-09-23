"""
Objetivo: configurar la conexión a la base de datos usando SQLAlchemy,
crear una sesión reutilizable y definir la base para los modelos ORM.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# ---------------------- ENGINE DE SQLALCHEMY ----------------------
# `create_engine` crea la conexión a la base de datos.
# `pool_pre_ping=True` revisa automáticamente si la conexión está viva antes de usarla

# Para que esto funcione correctamente, settings.DATABASE_URL debe contener:
# - root: usuario de MySQL
# - 1234: contraseña del usuario
# - localhost: host del servidor MySQL (puede ser IP o dominio)
# - 3306: puerto (por defecto MySQL)
# - biofiltros_db: ejemplo nombre de la base de datos
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# ---------------------- SESSION LOCAL ----------------------
# `sessionmaker` crea una clase de sesión que luego se puede instanciar.
# autocommit=False -> evita commits automáticos, se hace manualmente
# autoflush=False -> evita que los cambios se envíen automáticamente al DB
# bind=engine -> se vincula la sesión con nuestro engine creado
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------- BASE PARA MODELOS ----------------------
# Declarative base: todos los modelos ORM (clases de tablas) heredarán de Base para que SQLAlchemy pueda mapearlas a tablas en la base de datos
Base = declarative_base()


# ---------------------- DEPENDENCY PARA RUTAS ----------------------
# Esta función se usa como dependencia:
# - `db: Session = Depends(get_db)`
# - SessionLocal = Garantiza que cada request tenga su propia sesión y se cierre al terminar
# - `yield db` permite usarla en un `with` o directamente en el endpoint
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()