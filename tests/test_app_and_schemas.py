import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.schemas import (
    DiarioCreate,
    FeedbackUsabilidadCreate,
    UsuarioCreate,
)

client = TestClient(app)


def test_health_check_operativo():
    response = client.get("/")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["swagger_ui"] == "/docs"


def test_ruta_inexistente_usa_contrato_error_response():
    response = client.get("/api/v1/ruta-que-no-existe")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "NOT_FOUND"
    assert "details" in body["error"]


def test_openapi_expone_37_endpoints():
    paths = app.openapi()["paths"]
    total_endpoints = sum(len(metodos) for metodos in paths.values())
    assert total_endpoints == 37


def test_schemas_aceptan_alias_en_minuscula():
    usuario = UsuarioCreate(
        email="joven@colegio.edu.co",
        nombre="Ana Gómez",
        password="Password123",
    )
    assert usuario.Email == "joven@colegio.edu.co"
    assert usuario.Name == "Ana Gómez"

    entrada = DiarioCreate(emocion_id=2, nota_privada="Hoy necesité un respiro")
    assert entrada.Id_emocion == 2
    assert entrada.Nota_priv == "Hoy necesité un respiro"


def test_feedback_usabilidad_rechaza_calificacion_fuera_de_rango():
    with pytest.raises(ValidationError):
        FeedbackUsabilidadCreate(
            calificacion_facilidad=6,
            utilidad_percibida=4,
        )
