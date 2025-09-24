import hashlib
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.core.config import settings

def hash_password(password: str) -> str:
    """Genera hash SHA-256 de la contraseña"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verifica si el password ingresado coincide con el hash almacenado"""
    return hash_password(password) == hashed

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Genera un JWT firmado con SECRET_KEY"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str):
    """Decodifica un JWT y devuelve su payload"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
