import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.routers import (
    actividades,
    auth,
    bienestar,
    diagnostico,
    emociones,
    recursos,
    red_apoyo,
)
from app.schemas import ErrorDetail, ErrorResponse

logger = logging.getLogger("conectamente")

HTTP_ERROR_CODES = {
    status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
    status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
    status.HTTP_403_FORBIDDEN: "FORBIDDEN",
    status.HTTP_404_NOT_FOUND: "NOT_FOUND",
    status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
    status.HTTP_409_CONFLICT: "CONFLICT    ",
    status.HTTP_422_UNPROCESSABLE_CONTENT: "VALIDATION_ERROR",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "INTERNAL_SERVER_ERROR",
}

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Plataforma TIC para el bienestar emocional y la prevención "
        "de riesgos psicosociales en jóvenes."
    ),
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# MANEJADORES GLOBALES DE ERRORES (CONTRATO ErrorResponse)


def build_error_response(
    status_code: int,
    code: str,
    details: str,
    headers: dict | None = None,
) -> JSONResponse:
    payload = ErrorResponse(
        success=False,
        error=ErrorDetail(code=code, details=details),
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(),
        headers=headers,
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    code = HTTP_ERROR_CODES.get(exc.status_code, f"HTTP_{exc.status_code}")
    details = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return build_error_response(
        status_code=exc.status_code,
        code=code,
        details=details,
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errores_legibles = []
    for err in exc.errors():
        ruta_campo = " -> ".join(str(loc) for loc in err.get("loc", []) if loc != "body")
        mensaje = err.get("msg", "Valor inválido")
        if ruta_campo:
            errores_legibles.append(f"{ruta_campo}: {mensaje}")
        else:
            errores_legibles.append(mensaje)

    return build_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        code="VALIDATION_ERROR",
        details="; ".join(errores_legibles) or "Error de validación en los datos enviados",
    )


@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    logger.warning("Conflicto de integridad en MySQL: %s", exc.orig)
    details = (
        f"Conflicto de integridad en la base de datos: {exc.orig}"
        if settings.DEBUG
        else "La operación entra en conflicto con un registro existente o una restricción de datos."
    )
    return build_error_response(
        status_code=status.HTTP_409_CONFLICT,
        code="DATABASE_CONFLICT",
        details=details,
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.exception("Error de base de datos en %s", request.url.path)
    details = (
        f"Error de base de datos: {exc}"
        if settings.DEBUG
        else "No fue posible procesar la solicitud con la base de datos en este momento."
    )
    return build_error_response(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        code="DATABASE_ERROR",
        details=details,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Error interno no controlado en %s", request.url.path)
    details = (
        f"Error interno: {exc}" if settings.DEBUG else "Ocurrió un error inesperado en el servidor."
    )
    return build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_SERVER_ERROR",
        details=details,
    )


# REGISTRO DE ROUTERS MODULARES

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(emociones.router, prefix=settings.API_V1_PREFIX)
app.include_router(bienestar.router, prefix=settings.API_V1_PREFIX)
app.include_router(recursos.router, prefix=settings.API_V1_PREFIX)
app.include_router(actividades.router, prefix=settings.API_V1_PREFIX)
app.include_router(red_apoyo.router, prefix=settings.API_V1_PREFIX)
app.include_router(diagnostico.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Estado del Servidor"])
def health_check():
    return {
        "success": True,
        "message": f"{settings.APP_NAME} operativa",
        "version": settings.APP_VERSION,
        "swagger_ui": "/docs",
        "redoc": "/redoc",
    }
