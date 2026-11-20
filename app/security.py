from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

import bcrypt
from app import models
from app.config import settings
from app.database import get_db
from app.schemas import RolEnum, TokenData

# Configuración criptográfica
bearer_scheme = HTTPBearer(description="Token JWT en formato Bearer")

# 1. Utilidades de HASHING de contraseñas


def get_password_hash(password: str) -> str:
    """Genera un hash bcrypt con salt aleatoria (12 rondas)."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña plana contra su hash bcrypt almacenado."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        return False


# 2. Generacion y decodificacion de tokens jwt


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Crea un token JWT firmado con tiempo de expiración en UTC."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> TokenData:
    """Decodifica y valida la firma del token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: int | None = payload.get("sub")
        email: str | None = payload.get("email")
        rol: str | None = payload.get("rol")
        if user_id is None or email is None:
            raise credentials_exception
        return TokenData(user_id=int(user_id), email=email, rol=rol)
    except (JWTError, ValueError) as exc:
        raise credentials_exception from exc


# 3. Dependencias de autenticacion y autorizacion por roles RBAC


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.Usuario:
    """Obtiene el usuario autenticado actual desde MySQL y verifica que esté activo."""
    token_data = decode_access_token(credentials.credentials)
    usuario = (
        db.query(models.Usuario).filter(models.Usuario.Id_usuario == token_data.user_id).first()
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

    def __init__(self, allowed_roles: list[str]):
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
