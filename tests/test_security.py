from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hash_usa_salt_dinamica_y_verifica():
    password_plana = "ConectaMente2026*"
    hash_1 = get_password_hash(password_plana)
    hash_2 = get_password_hash(password_plana)

    assert hash_1 != password_plana
    assert hash_1 != hash_2  # Cada ejecución genera una salt única
    assert verify_password(password_plana, hash_1) is True
    assert verify_password(password_plana, hash_2) is True
    assert verify_password("ClaveIncorrecta", hash_1) is False


def test_crear_y_decodificar_jwt_valido():
    token = create_access_token(
        data={
            "sub": "42",
            "email": "estudiante@colegio.edu.co",
            "rol": "Estudiante",
        }
    )

    token_data = decode_access_token(token)
    assert token_data.user_id == 42
    assert token_data.email == "estudiante@colegio.edu.co"
    assert token_data.rol == "Estudiante"


def test_jwt_expirado_lanza_401():
    token_expirado = create_access_token(
        data={"sub": "1", "email": "admin@conectamente.edu.co", "rol": "admin"},
        expires_delta=timedelta(seconds=-10),
    )

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(token_expirado)

    assert exc_info.value.status_code == 401


def test_jwt_manipulado_lanza_401():
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token("token.invalido.firmado_mal")

    assert exc_info.value.status_code == 401
