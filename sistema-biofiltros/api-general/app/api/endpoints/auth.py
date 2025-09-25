from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import Usuario
from app.schemas.login import LoginData
from app.schemas.token import Token
from app.schemas.user import UsuarioResponse
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

# ---------------------- ROUTER ----------------------
router = APIRouter(tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------------------- ENDPOINTS ----------------------
@router.post("/login", response_model=Token)
def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña inválidos"
        )
    
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UsuarioResponse)
def get_current_user(
    token: str = Query(..., description="Token JWT obtenido al iniciar sesión"),  # ahora obligatorio en query
    db: Session = Depends(get_db)
):
    """
    Endpoint protegido para pruebas: se pasa el token directamente como query param.
    Ejemplo:
    /me?token=<TU_TOKEN>
    """
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    
    username = payload.get("sub")
    user = db.query(Usuario).filter(Usuario.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    
    return user