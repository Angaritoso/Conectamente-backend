import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas import TokenData, RolEnum

load_dotenv()

# Configuración criptográfica
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(description="Token JWT en formato Bearer")

SECRET_KEY = os.getenv("SECRET_KEY", "conectamente_secret_key_temporal_2026")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))


# 1. Utilidades de HASHING de contraseñas

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña en texto plano coincide con el hash almacenado."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Genera un hash seguro con bcrypt para almacenar en Usuario.Password_hash."""
    return pwd_context.hash(password)


# 2. Generacion y decodificacion de tokens jwt

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT firmado con tiempo de expiración en UTC."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> TokenData:
    """Decodifica y valida la firma del token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[int] = payload.get("sub")
        email: Optional[str] = payload.get("email")
        rol: Optional[str] = payload.get("rol")
        if user_id is None or email is None:
            raise credentials_exception
        return TokenData(user_id=int(user_id), email=email, rol=rol)
    except (JWTError, ValueError):
        raise credentials_exception


# 3. Dependencias de autenticacion y autorizacion por roles RBAC

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> models.Usuario:
    """Obtiene el usuario autenticado actual desde MySQL y verifica que esté activo."""
    token_data = decode_access_token(credentials.credentials)
    usuario = (
        db.query(models.Usuario)
        .filter(models.Usuario.Id_usuario == token_data.user_id)
        .first()
    )
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El usuario asociado al token no existe",
        )
    if not usuario.Estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta de usuario se encuentra inactiva",
        )
    return usuario


class RoleChecker:
    """Validador reutilizable de permisos según los actores del diagrama de Casos de Uso."""

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: models.Usuario = Depends(get_current_user)) -> models.Usuario:
        if current_user.Rol not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permisos insuficientes. Se requiere uno de los roles: {', '.join(self.allowed_roles)}",
            )
        return current_user


# Dependencias listas para inyectar en los routers según CasosDeUso_Conectamente.mdj:
require_authenticated = get_current_user
require_admin = RoleChecker([RolEnum.admin.value])
require_orientador = RoleChecker([RolEnum.orientador.value])
require_staff = RoleChecker([RolEnum.admin.value, RolEnum.orientador.value])