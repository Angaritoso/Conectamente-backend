from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import (
    EncuestaDiagnosticoCreate,
    EncuestaDiagnosticoOut,
    FeedbackUsabilidadCreate,
    FeedbackUsabilidadOut,
    StandardResponse,
)
from app.security import require_staff

router = APIRouter(tags=["Métricas y Evaluación"])


# =========================================================================
# SECCIÓN A: RECOLECCIÓN ANÓNIMA (SIN AUTENTICACIÓN NI TRAZABILIDAD DE USUARIO)
# =========================================================================


@router.post(
    "/anonimo/diagnostico", response_model=StandardResponse, status_code=status.HTTP_201_CREATED
)
def registrar_encuesta_diagnostico(datos: EncuestaDiagnosticoCreate, db: Session = Depends(get_db)):
    """
    Caso de Uso: ResponderEncuestaDiagnostico (Fase 1: Diagnóstico).
    Guarda un registro 100% anónimo e independiente en la tabla Encuesta_diagnostico.
    """
    nueva_encuesta = models.EncuestaDiagnostico(
        Rango_edad=datos.Rango_edad,
        Necesidad_principal=datos.Necesidad_principal,
        Detalles=datos.Detalles,
    )
    db.add(nueva_encuesta)
    db.commit()
    db.refresh(nueva_encuesta)

    return StandardResponse(
        success=True,
        data=EncuestaDiagnosticoOut.model_validate(nueva_encuesta).model_dump(),
        message="Encuesta diagnóstica registrada de forma anónima",
    )


@router.post(
    "/anonimo/usabilidad", response_model=StandardResponse, status_code=status.HTTP_201_CREATED
)
def registrar_feedback_usabilidad(datos: FeedbackUsabilidadCreate, db: Session = Depends(get_db)):
    """
    Caso de Uso: EnviarFeedbackUsabilidad (Fases 4 y 5: Prueba y Evaluación).
    Guarda la percepción de facilidad de uso y utilidad de forma anónima en Feedback_usabilidad.
    """
    nuevo_feedback = models.FeedbackUsabilidad(
        Calificacion_facilidad=datos.Calificacion_facilidad,
        Utilidad_percibida=datos.Utilidad_percibida,
        Comentario_mejora=datos.Comentario_mejora,
    )
    db.add(nuevo_feedback)
    db.commit()
    db.refresh(nuevo_feedback)

    return StandardResponse(
        success=True,
        data=FeedbackUsabilidadOut.model_validate(nuevo_feedback).model_dump(),
        message="Feedback de usabilidad registrado de forma anónima",
    )


# =========================================================================
# SECCIÓN B: PANEL DE MÉTRICAS Y REPORTES AGREGADOS (ADMIN Y ORIENTADOR)
# =========================================================================


@router.get("/metrics/dashboard", response_model=StandardResponse)
def obtener_metricas_consolidadas(
    db: Session = Depends(get_db), current_user: models.Usuario = Depends(require_staff)
):
    """
    Casos de Uso: VisualizarReportesYEstadisticas / CUE; AnalizarMetricasSalud.
    Consolida estadísticas de necesidades emocionales (Fase 1) y usabilidad (Fase 5)
    para toma de decisiones del Orientador y del Administrador.
    """
    # 1. Métricas agregadas de la Encuesta Diagnóstica (Fase 1)
    total_diagnosticos = db.query(func.count(models.EncuestaDiagnostico.Id_encuesta)).scalar() or 0

    conteo_por_necesidad = (
        db.query(
            models.EncuestaDiagnostico.Necesidad_principal,
            func.count(models.EncuestaDiagnostico.Id_encuesta).label("cantidad"),
        )
        .group_by(models.EncuestaDiagnostico.Necesidad_principal)
        .order_by(func.count(models.EncuestaDiagnostico.Id_encuesta).desc())
        .all()
    )

    conteo_por_edad = (
        db.query(
            models.EncuestaDiagnostico.Rango_edad,
            func.count(models.EncuestaDiagnostico.Id_encuesta).label("cantidad"),
        )
        .group_by(models.EncuestaDiagnostico.Rango_edad)
        .order_by(models.EncuestaDiagnostico.Rango_edad.asc())
        .all()
    )

    ultimos_diagnosticos = (
        db.query(models.EncuestaDiagnostico)
        .order_by(models.EncuestaDiagnostico.Fecha_creacion.desc())
        .limit(10)
        .all()
    )

    # 2. Métricas agregadas de Feedback de Usabilidad (Fases 4 y 5)
    total_feedback = db.query(func.count(models.FeedbackUsabilidad.Id_feedback)).scalar() or 0

    promedios_usabilidad = db.query(
        func.avg(models.FeedbackUsabilidad.Calificacion_facilidad).label("promedio_facilidad"),
        func.avg(models.FeedbackUsabilidad.Utilidad_percibida).label("promedio_utilidad"),
    ).first()

    promedio_facilidad = (
        round(float(promedios_usabilidad.promedio_facilidad), 2)
        if promedios_usabilidad and promedios_usabilidad.promedio_facilidad is not None
        else 0.0
    )
    promedio_utilidad = (
        round(float(promedios_usabilidad.promedio_utilidad), 2)
        if promedios_usabilidad and promedios_usabilidad.promedio_utilidad is not None
        else 0.0
    )

    ultimos_comentarios = (
        db.query(models.FeedbackUsabilidad)
        .order_by(models.FeedbackUsabilidad.Fecha_creacion.desc())
        .limit(10)
        .all()
    )

    reporte_consolidado = {
        "diagnostico_fase_1": {
            "total_respuestas": total_diagnosticos,
            "distribucion_necesidades": [
                {"necesidad_principal": item.Necesidad_principal, "cantidad": item.cantidad}
                for item in conteo_por_necesidad
            ],
            "distribucion_edades": [
                {"rango_edad": item.Rango_edad, "cantidad": item.cantidad}
                for item in conteo_por_edad
            ],
            "registros_recientes": [
                EncuestaDiagnosticoOut.model_validate(d).model_dump() for d in ultimos_diagnosticos
            ],
        },
        "evaluacion_usabilidad_fase_5": {
            "total_evaluaciones": total_feedback,
            "promedio_facilidad_uso": promedio_facilidad,
            "promedio_utilidad_percibida": promedio_utilidad,
            "escala_maxima": 5,
            "comentarios_recientes": [
                FeedbackUsabilidadOut.model_validate(f).model_dump() for f in ultimos_comentarios
            ],
        },
    }

    return StandardResponse(
        success=True,
        data=reporte_consolidado,
        message="Métricas consolidadas del sistema generadas correctamente",
    )
