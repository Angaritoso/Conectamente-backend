from typing import Dict, List
from fastapi import APIRouter, HTTPException, status

from app.schemas import (
    DimensionBienestarEnum,
    EvaluacionFeedbackOut,
    EvaluacionIn,
    PreguntaReflexionOut,
    ResultadoDimensionOut,
    StandardResponse,
)

router = APIRouter(prefix="/bienestar", tags=["Módulo 2 - Bienestar"])

# Catálogo estático en memoria con las 5 dimensiones del proyecto ConectaMente

BANCO_PREGUNTAS_REFLEXION: List[PreguntaReflexionOut] = [
    PreguntaReflexionOut(
        pregunta_id=1,
        dimension=DimensionBienestarEnum.estado_animo,
        #Sujeto a cambios de escritura para enunciado
        #Preferiblemente preguntas planteadas por profesional, etapa de prueba
        enunciado="Durante esta semana, ¿con qué frecuencia te has sentido desmotivado, triste o con cambios bruscos de humor?",
    ),
    PreguntaReflexionOut(
        pregunta_id=2,
        dimension=DimensionBienestarEnum.estado_animo,
        #Enunciado sujetoo a cambios 
        enunciado="¿Qué tan difícil te ha resultado disfrutar de tus actividades cotidianas o pasatiempos?",
    ),
    PreguntaReflexionOut(
        pregunta_id=3,
        dimension=DimensionBienestarEnum.estres_academico,
        #Enunciado sujetoo a cambios 
        enunciado="¿Te has sentido abrumado o sobrepasado por la carga de tareas, proyectos o exámenes?",
    ),
    PreguntaReflexionOut(
        pregunta_id=4,
        dimension=DimensionBienestarEnum.estres_academico,
        #Enunciado sujetoo a cambios 
        enunciado="¿Sientes tensión física o preocupación constante cuando piensas en tus responsabilidades de estudio?",
    ),
    PreguntaReflexionOut(
        pregunta_id=5,
        dimension=DimensionBienestarEnum.relaciones_interpersonales,
        #Enunciado sujetoo a cambios 
        enunciado="¿Has tenido dificultades para comunicarte o resolver desacuerdos con tu familia o compañeros?",
    ),
    PreguntaReflexionOut(
        pregunta_id=6,
        dimension=DimensionBienestarEnum.relaciones_interpersonales,
        #Enunciado sujetoo a cambios 
        enunciado="¿Te has sentido aislado o incomprendido dentro de tu entorno escolar o social?",
    ),
    PreguntaReflexionOut(
        pregunta_id=7,
        dimension=DimensionBienestarEnum.habitos_descanso,
        #Enunciado sujetoo a cambios 
        enunciado="¿Has tenido dificultad para conciliar el sueño o sientes que tu descanso no es reparador?",
    ),
    PreguntaReflexionOut(
        pregunta_id=8,
        dimension=DimensionBienestarEnum.habitos_descanso,
        #Enunciado sujetoo a cambios 
        enunciado="¿Con qué frecuencia postergas tus horas de sueño por usar el celular o estudiar hasta tarde?",
    ),
    PreguntaReflexionOut(
        pregunta_id=9,
        dimension=DimensionBienestarEnum.apoyo_social,
        #Enunciado sujetoo a cambios 
        enunciado="Cuando enfrentas un problema personal, ¿sientes que te falta alguien de confianza con quien hablar?",
    ),
    PreguntaReflexionOut(
        pregunta_id=10,
        dimension=DimensionBienestarEnum.apoyo_social,
        #Enunciado sujetoo a cambios 
        enunciado="¿Sientes dudas o temor de acudir a un orientador, docente o adulto responsable cuando necesitas ayuda?",
    ),
]

MAPA_PREGUNTAS: Dict[int, PreguntaReflexionOut] = {
    p.pregunta_id: p for p in BANCO_PREGUNTAS_REFLEXION
}

#Recomendaciones sujetas a cambios antes de pasar por calidad final 
RECOMENDACIONES_POR_DIMENSION: Dict[DimensionBienestarEnum, str] = {
    DimensionBienestarEnum.estado_animo: (
        "Explora el Módulo 1 (Conoce tus emociones) y utiliza el Diario Privado del Módulo 4 "
        "para expresar y reconocer lo que sientes día a día."
    ),
    DimensionBienestarEnum.estres_academico: (
        "Consulta las guías de 'Organización del tiempo' y 'Manejo del estrés' en la Biblioteca Aprende (Módulo 3), "
        "y practica los ejercicios de respiración guiada del Módulo 4."
    ),
    DimensionBienestarEnum.relaciones_interpersonales: (
        "Revisa las lecturas sobre 'Comunicación asertiva' y 'Resolución de conflictos' en el Módulo 3 "
        "para fortalecer tus vínculos cotidianos."
    ),
    DimensionBienestarEnum.habitos_descanso: (
        "Establece una rutina de desconexión digital 30 minutos antes de dormir y apóyate en "
        "las actividades de relajación del Módulo 4."
    ),
    DimensionBienestarEnum.apoyo_social: (
        "Recuerda que no tienes que afrontar todo en soledad: visita el Módulo 5 (Red de Apoyo) "
        "para conocer los canales de escucha y orientación disponibles en tu institución."
    ),
}


@router.get("/cuestionario", response_model=StandardResponse)
def obtener_cuestionario_reflexion():
    """Devuelve las preguntas interactivas de autorreflexión agrupadas en las 5 dimensiones."""
    return StandardResponse(
        success=True,
        data=[p.model_dump() for p in BANCO_PREGUNTAS_REFLEXION],
        message="Cuestionario de autorreflexión cargado correctamente",
    )


@router.post("/evaluar", response_model=StandardResponse)
def evaluar_bienestar_en_memoria(datos: EvaluacionIn):
    """
    Caso de Uso: TestAutorreflexion <<include>> VisualizarRetroalimentacion.
    Procesa las respuestas 100% en memoria volátil sin persistir ningún dato en MySQL.
    """
    acumulado_dimension: Dict[DimensionBienestarEnum, List[int]] = {}

    for item in datos.respuestas:
        pregunta = MAPA_PREGUNTAS.get(item.pregunta_id)
        if not pregunta:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El pregunta_id {item.pregunta_id} no existe en el cuestionario oficial.",
            )
        acumulado_dimension.setdefault(pregunta.dimension, []).append(item.valor)

    desglose: List[ResultadoDimensionOut] = []
    recomendaciones_personalizadas: List[str] = []

    for dimension, valores in acumulado_dimension.items():
        prom_dim = round(sum(valores) / len(valores), 2)
        if prom_dim >= 3.8:
            estado_dim = "Atención prioritaria"
            obs_dim = f"Se identifica una sobrecarga importante en {dimension.value.lower()}."
            recomendaciones_personalizadas.append(RECOMENDACIONES_POR_DIMENSION[dimension])
        elif prom_dim >= 2.5:
            estado_dim = "Alerta moderada"
            obs_dim = f"Presentas señales moderadas en {dimension.value.lower()} que vale la pena atender."
            recomendaciones_personalizadas.append(RECOMENDACIONES_POR_DIMENSION[dimension])
        else:
            estado_dim = "Equilibrado"
            obs_dim = f"Tus indicadores actuales en {dimension.value.lower()} son favorables."

        desglose.append(
            ResultadoDimensionOut(
                dimension=dimension.value,
                promedio=prom_dim,
                estado=estado_dim,
                observacion=obs_dim,
            )
        )

    puntaje_total = sum(item.valor for item in datos.respuestas)
    promedio_general = round(puntaje_total / len(datos.respuestas), 2)

    if promedio_general >= 3.8:
        nivel_general = "Sobrecarga Emocional Alta"
        sugerir_red = True
        recomendaciones_personalizadas.append(
            "Considera conversar pronto con un orientador escolar o persona de confianza a través del Módulo 5 (Red de Apoyo)."
        )
    elif promedio_general >= 2.5:
        nivel_general = "Carga Emocional Moderada"
        sugerir_red = False
    else:
        nivel_general = "Bienestar Equilibrado"
        sugerir_red = False
        if not recomendaciones_personalizadas:
            recomendaciones_personalizadas.append(
                "Continúa fortaleciendo tus hábitos de autocuidado y explora la Biblioteca Aprende (Módulo 3)."
            )

    resultado = EvaluacionFeedbackOut(
        nivel_general=nivel_general,
        puntaje_promedio=promedio_general,
        desglose_dimensiones=desglose,
        recomendaciones=recomendaciones_personalizadas,
        sugerir_red_apoyo=sugerir_red,
    )

    return StandardResponse(
        success=True,
        data=resultado.model_dump(),
        message="Autorreflexión procesada en memoria con éxito (ningún dato personal fue almacenado)",
    )