import os
import requests

from frontend.state import get_token

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
TIMEOUT = 10


def _headers(auth: bool = False) -> dict:
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if auth:
        token = get_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
    return headers


def _handle_response(response: requests.Response) -> tuple[bool, dict | list | None, str]:
    if response.status_code == 204:
        return True, None, "Operación realizada correctamente"

    try:
        payload = response.json()
    except ValueError:
        return False, None, f"Error HTTP {response.status_code} (respuesta no JSON)"

    if response.ok and (not isinstance(payload, dict) or payload.get("success", True)):
        if isinstance(payload, dict):
            return True, payload.get("data", payload), payload.get("message", "OK")
        return True, payload, "OK"

    error_info = payload.get("error", {}) if isinstance(payload, dict) else {}
    detail = (
        error_info.get("details")
        if isinstance(error_info, dict) and error_info.get("details")
        else (payload.get("detail") if isinstance(payload, dict) else None)
    )

    if isinstance(detail, list):
        partes = []
        for err in detail:
            if isinstance(err, dict):
                loc = ".".join(str(x) for x in err.get("loc", []) if x != "body")
                partes.append(f"{loc}: {err.get('msg', '')}")
            else:
                partes.append(str(err))
        detail = " | ".join(partes)

    return False, None, str(detail or f"Error HTTP {response.status_code}")


def api_request(
    method: str,
    endpoint: str,
    *,
    json: dict | None = None,
    params: dict | None = None,
    auth: bool = False,
) -> tuple[bool, dict | list | None, str]:
    url = f"{API_BASE_URL}{endpoint}"
    try:
        resp = requests.request(
            method=method,
            url=url,
            json=json,
            params=params,
            headers=_headers(auth=auth),
            timeout=TIMEOUT,
        )
        return _handle_response(resp)
    except requests.ConnectionError:
        return False, None, "No se pudo conectar con la API. Verifica que FastAPI esté activo en el puerto 8000."
    except requests.Timeout:
        return False, None, "La API tardó demasiado en responder."


# --- Autenticación ---
def login(email: str, password: str):
    return api_request("POST", "/auth/login", json={"Email": email, "Password": password})


def register(name: str, email: str, password: str):
    return api_request("POST", "/auth/register", json={"Name": name, "Email": email, "Password": password})


def get_me():
    return api_request("GET", "/auth/me", auth=True)


# --- Red de Apoyo (SOS) ---
def get_emergencias():
    return api_request("GET", "/red-apoyo/emergencias")


def get_red_apoyo():
    return api_request("GET", "/red-apoyo")


# --- Emociones y Diario Privado ---
def get_emociones():
    return api_request("GET", "/emociones")


def get_diario():
    return api_request("GET", "/diario", auth=True)


def create_diario(data: dict):
    return api_request("POST", "/diario", json=data, auth=True)


def delete_diario(diario_id: int):
    return api_request("DELETE", f"/diario/{diario_id}", auth=True)


# --- Bienestar ---
def get_cuestionario_bienestar():
    return api_request("GET", "/bienestar/cuestionario")


def evaluar_bienestar(data: dict):
    return api_request("POST", "/bienestar/evaluar", json=data)


# --- Recursos Educativos y Actividades ---
def get_recursos():
    return api_request("GET", "/recursos")


def create_recurso(data: dict):
    return api_request("POST", "/recursos", json=data, auth=True)


def delete_recurso(recurso_id: int):
    return api_request("DELETE", f"/recursos/{recurso_id}", auth=True)


def get_actividades():
    return api_request("GET", "/actividades")


def create_actividad(data: dict):
    return api_request("POST", "/actividades", json=data, auth=True)


def delete_actividad(actividad_id: int):
    return api_request("DELETE", f"/actividades/{actividad_id}", auth=True)


# --- Encuestas Anónimas y Dashboard ---
def enviar_diagnostico(data: dict):
    return api_request("POST", "/anonimo/diagnostico", json=data)


def enviar_usabilidad(data: dict):
    return api_request("POST", "/anonimo/usabilidad", json=data)


def get_dashboard_metrics():
    return api_request("GET", "/metrics/dashboard", auth=True)