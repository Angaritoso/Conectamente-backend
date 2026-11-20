from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import (
    EmocionCreate,
    EmocionOut,
    EmocionUpdate,
    StandardResponse,
)
from app.security import require_admin, require_staff

router = APIRouter(prefix="/emociones", tags=["Módulo 1 - Emociones"])


@router.get("", response_model=StandardResponse)
def listar_emociones(buscar: str | None = None, db: Session = Depends(get_db)):
    """
    Caso de Uso: ConsultarCatalogoEmocion.
    Devuelve el catálogo de emociones primarias (alegría, tristeza, miedo, enojo, frustración, preocupación).
    """
    query = db.query(models.Emocion)
    if buscar:
        query = query.filter(models.Emocion.Nombre.ilike(f"%{buscar}%"))

    emociones = query.order_by(models.Emocion.Id_emocion.asc()).all()
    data = [EmocionOut.model_validate(e).model_dump() for e in emociones]

    return StandardResponse(
        success=True, data=data, message="Catálogo de emociones obtenido correctamente"
    )


@router.get("/{emocion_id}", response_model=StandardResponse)
def obtener_emocion(emocion_id: int, db: Session = Depends(get_db)):
    """Obtiene el detalle y las estrategias de afrontamiento de una emoción específica."""
    emocion = db.query(models.Emocion).filter(models.Emocion.Id_emocion == emocion_id).first()
    if not emocion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La emoción con ID {emocion_id} no existe",
        )

    return StandardResponse(
        success=True,
        data=EmocionOut.model_validate(emocion).model_dump(),
        message="Detalle de la emoción obtenido con éxito",
    )


@router.post("", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def crear_emocion(
    datos: EmocionCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_staff),
):
    """Registra una nueva emoción en el catálogo (Solo Admin u Orientador)."""
    existente = db.query(models.Emocion).filter(models.Emocion.Nombre == datos.Nombre).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una emoción registrada con el nombre '{datos.Nombre}'",
        )

    nueva_emocion = models.Emocion(
        Nombre=datos.Nombre,
        Descripcion=datos.Descripcion,
        Estrategias_afrontamiento=datos.Estrategias_afrontamiento,
        Icono_url=datos.Icono_url,
    )
    db.add(nueva_emocion)
    db.commit()
    db.refresh(nueva_emocion)

    return StandardResponse(
        success=True,
        data=EmocionOut.model_validate(nueva_emocion).model_dump(),
        message="Emoción registrada exitosamente",
    )


@router.put("/{emocion_id}", response_model=StandardResponse)
def actualizar_emocion(
    emocion_id: int,
    datos: EmocionUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_staff),
):
    """Actualiza la descripción o estrategias de afrontamiento de una emoción (Solo Admin u Orientador)."""
    emocion = db.query(models.Emocion).filter(models.Emocion.Id_emocion == emocion_id).first()
    if not emocion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La emoción con ID {emocion_id} no existe",
        )

    campos_actualizados = datos.model_dump(exclude_unset=True)
    for campo, valor in campos_actualizados.items():
        setattr(emocion, campo, valor)

    db.commit()
    db.refresh(emocion)

    return StandardResponse(
        success=True,
        data=EmocionOut.model_validate(emocion).model_dump(),
        message="Emoción actualizada correctamente",
    )


@router.delete("/{emocion_id}", response_model=StandardResponse)
def eliminar_emocion(
    emocion_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_admin),
):
    """Elimina una emoción del catálogo si no tiene entradas de diario asociadas (Solo Admin)."""
    emocion = db.query(models.Emocion).filter(models.Emocion.Id_emocion == emocion_id).first()
    if not emocion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La emoción con ID {emocion_id} no existe",
        )

    entradas_asociadas = (
        db.query(models.DiarioEmocionUsuario)
        .filter(models.DiarioEmocionUsuario.Id_emocion == emocion_id)
        .count()
    )
    if entradas_asociadas > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar esta emoción porque existen entradas de diario que hacen referencia a ella",
        )

    db.delete(emocion)
    db.commit()

    return StandardResponse(success=True, data=None, message="Emoción eliminada correctamente")
