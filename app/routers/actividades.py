from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import (
    ActividadCreate,
    ActividadOut,
    ActividadUpdate,
    DiarioCreate,
    DiarioOut,
    StandardResponse,
)
from app.security import require_admin, require_authenticated

router = APIRouter(tags=["Módulo 4 - Diario y Actividades"])


# SECCIÓN A: ACTIVIDADES INTERACTIVAS GUIADAS (/actividades)


@router.get("/actividades", response_model=StandardResponse)
def listar_actividades(
    tipo_actividad: str | None = None, emocion_id: int | None = None, db: Session = Depends(get_db)
):
    """
    Caso de Uso: RealizarActividadesGuiadas.
    Lista los ejercicios de respiración, reflexión y dinámicas de comunicación.
    """
    query = db.query(models.ActividadesInteractivas)

    if tipo_actividad:
        query = query.filter(
            models.ActividadesInteractivas.Tipo_actividad.ilike(f"%{tipo_actividad}%")
        )
    if emocion_id is not None:
        query = query.filter(models.ActividadesInteractivas.Id_emocion == emocion_id)

    actividades = query.order_by(models.ActividadesInteractivas.Id_actividades.asc()).all()
    data = [ActividadOut.model_validate(a).model_dump() for a in actividades]

    return StandardResponse(
        success=True, data=data, message="Actividades interactivas obtenidas correctamente"
    )


@router.get("/actividades/{actividad_id}", response_model=StandardResponse)
def obtener_actividad(actividad_id: int, db: Session = Depends(get_db)):
    """Obtiene las instrucciones detalladas y duración estimada de una actividad guiada."""
    actividad = (
        db.query(models.ActividadesInteractivas)
        .filter(models.ActividadesInteractivas.Id_actividades == actividad_id)
        .first()
    )
    if not actividad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La actividad con ID {actividad_id} no existe",
        )

    return StandardResponse(
        success=True,
        data=ActividadOut.model_validate(actividad).model_dump(),
        message="Actividad obtenida con éxito",
    )


@router.post("/actividades", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def crear_actividad(
    datos: ActividadCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_admin),
):
    """
    Caso de Uso: GestionarActividadesInteractivas.
    Crea una nueva actividad interactiva validando la emoción opcional asociada (0..1 a 0..*).
    """
    if datos.Id_emocion is not None:
        emocion = (
            db.query(models.Emocion).filter(models.Emocion.Id_emocion == datos.Id_emocion).first()
        )
        if not emocion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La emoción asociada con ID {datos.Id_emocion} no existe",
            )

    nueva_actividad = models.ActividadesInteractivas(
        Id_admin=current_user.Id_usuario,
        Id_emocion=datos.Id_emocion,
        Titulo=datos.Titulo,
        Tipo_actividad=datos.Tipo_actividad,
        Instrucciones=datos.Instrucciones,
        Duracion_estimada=datos.Duracion_estimada,
    )
    db.add(nueva_actividad)
    db.commit()
    db.refresh(nueva_actividad)

    return StandardResponse(
        success=True,
        data=ActividadOut.model_validate(nueva_actividad).model_dump(),
        message="Actividad interactiva creada correctamente",
    )


@router.put("/actividades/{actividad_id}", response_model=StandardResponse)
def actualizar_actividad(
    actividad_id: int,
    datos: ActividadUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_admin),
):
    """Actualiza una actividad interactiva existente (Solo Admin)."""
    actividad = (
        db.query(models.ActividadesInteractivas)
        .filter(models.ActividadesInteractivas.Id_actividades == actividad_id)
        .first()
    )
    if not actividad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La actividad con ID {actividad_id} no existe",
        )

    if datos.Id_emocion is not None:
        emocion = (
            db.query(models.Emocion).filter(models.Emocion.Id_emocion == datos.Id_emocion).first()
        )
        if not emocion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La emoción asociada con ID {datos.Id_emocion} no existe",
            )

    campos_actualizados = datos.model_dump(exclude_unset=True)
    for campo, valor in campos_actualizados.items():
        setattr(actividad, campo, valor)

    db.commit()
    db.refresh(actividad)

    return StandardResponse(
        success=True,
        data=ActividadOut.model_validate(actividad).model_dump(),
        message="Actividad interactiva actualizada correctamente",
    )


@router.delete("/actividades/{actividad_id}", response_model=StandardResponse)
def eliminar_actividad(
    actividad_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_admin),
):
    """Elimina una actividad interactiva (Solo Admin)."""
    actividad = (
        db.query(models.ActividadesInteractivas)
        .filter(models.ActividadesInteractivas.Id_actividades == actividad_id)
        .first()
    )
    if not actividad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La actividad con ID {actividad_id} no existe",
        )

    db.delete(actividad)
    db.commit()

    return StandardResponse(
        success=True, data=None, message="Actividad interactiva eliminada correctamente"
    )


# SECCIÓN B: DIARIO EMOCIONAL PRIVADO DEL USUARIO (/diario)


@router.get("/diario", response_model=StandardResponse)
def listar_entradas_diario(
    db: Session = Depends(get_db), current_user: models.Usuario = Depends(require_authenticated)
):
    """
    Devuelve exclusivamente las entradas privadas pertenecientes al usuario autenticado.
    """
    entradas = (
        db.query(models.DiarioEmocionUsuario)
        .filter(models.DiarioEmocionUsuario.id_usuario == current_user.Id_usuario)
        .order_by(models.DiarioEmocionUsuario.Fecha_registro.desc())
        .all()
    )
    data = [DiarioOut.model_validate(e).model_dump() for e in entradas]

    return StandardResponse(
        success=True, data=data, message="Historial del diario privado cargado correctamente"
    )


@router.post("/diario", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def crear_entrada_diario(
    datos: DiarioCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_authenticated),
):
    """
    Caso de Uso: EscribirEntradaDiario <<include>> IniciarSesion.
    Guarda una nueva nota privada vinculada al usuario autenticado y a una emoción existente.
    """
    emocion = db.query(models.Emocion).filter(models.Emocion.Id_emocion == datos.Id_emocion).first()
    if not emocion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La emoción con ID {datos.Id_emocion} no existe en el catálogo",
        )

    nueva_entrada = models.DiarioEmocionUsuario(
        id_usuario=current_user.Id_usuario,
        Id_emocion=datos.Id_emocion,
        Nota_priv=datos.Nota_priv,
    )
    db.add(nueva_entrada)
    db.commit()
    db.refresh(nueva_entrada)

    return StandardResponse(
        success=True,
        data=DiarioOut.model_validate(nueva_entrada).model_dump(),
        message="Entrada guardada correctamente en tu diario privado",
    )


@router.delete("/diario/{diario_id}", response_model=StandardResponse)
def eliminar_entrada_diario(
    diario_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_authenticated),
):
    """Permite al usuario eliminar únicamente una entrada propia de su diario privado."""
    entrada = (
        db.query(models.DiarioEmocionUsuario)
        .filter(
            models.DiarioEmocionUsuario.Id_diario_usuario == diario_id,
            models.DiarioEmocionUsuario.id_usuario == current_user.Id_usuario,
        )
        .first()
    )
    if not entrada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La entrada de diario no existe o no pertenece a tu cuenta",
        )

    db.delete(entrada)
    db.commit()

    return StandardResponse(
        success=True, data=None, message="Entrada del diario eliminada correctamente"
    )
