from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_obtener_cuestionario_reflexion():
    response = client.get("/api/v1/bienestar/cuestionario")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 10

    dimensiones = {p["dimension"] for p in body["data"]}
    assert len(dimensiones) == 5


def test_evaluar_bienestar_equilibrado():
    payload = {"respuestas": [{"pregunta_id": i, "valor": 1} for i in range(1, 11)]}
    response = client.post("/api/v1/bienestar/evaluar", json=payload)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["nivel_general"] == "Bienestar Equilibrado"
    assert data["puntaje_promedio"] == 1.0
    assert data["sugerir_red_apoyo"] is False
    assert "no constituye un diagnóstico" in data["aviso_etico"].lower()


def test_evaluar_bienestar_carga_moderada():
    payload = {"respuestas": [{"pregunta_id": i, "valor": 3} for i in range(1, 11)]}
    response = client.post("/api/v1/bienestar/evaluar", json=payload)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["nivel_general"] == "Carga Emocional Moderada"
    assert data["puntaje_promedio"] == 3.0
    assert data["sugerir_red_apoyo"] is False
    assert len(data["recomendaciones"]) >= 1


def test_evaluar_bienestar_sobrecarga_alta_sugiere_red_apoyo():
    payload = {"respuestas": [{"pregunta_id": i, "valor": 5} for i in range(1, 11)]}
    response = client.post("/api/v1/bienestar/evaluar", json=payload)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["nivel_general"] == "Sobrecarga Emocional Alta"
    assert data["puntaje_promedio"] == 5.0
    assert data["sugerir_red_apoyo"] is True


def test_evaluar_bienestar_valor_fuera_de_rango_devuelve_error_estandar():
    payload = {"respuestas": [{"pregunta_id": 1, "valor": 6}]}
    response = client.post("/api/v1/bienestar/evaluar", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
