from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import (
    RecursoCreate,
    RecursoOut,
    RecursoUpdate,
    StandardResponse,
)
from app.security import require_admin, require_staff

router = APIRouter(prefix="/recursos", tags=["Módulo 3 - Aprende"])


@router.get("", response_model=StandardResponse)
def listar_recursos(
    categoria: str | None = None,
    buscar: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Caso de Uso: LeerRecursosEducativos.
    Lista los artículos de la biblioteca digital con filtro opcional por categoría o título.
    """
    query = db.query(models.RecursoEducativo)

    if categoria:
        query = query.filter(models.RecursoEducativo.Categoria.ilike(f"%{categoria}%"))
    if buscar:
        query = query.filter(models.RecursoEducativo.Titulo.ilike(f"%{buscar}%"))

    recursos = query.order_by(models.RecursoEducativo.Fecha_publicacion.desc()).all()
    data = [RecursoOut.model_validate(r).model_dump() for r in recursos]

    return StandardResponse(
        success=True,
        data=data,
        message="Recursos educativos obtenidos con éxito",
    )


@router.get("/{recurso_id}", response_model=StandardResponse)
def obtener_recurso(recurso_id: int, db: Session = Depends(get_db)):
    """Obtiene el contenido completo en Markdown de un recurso educativo específico."""
    recurso = (
        db.query(models.RecursoEducativo)
        .filter(models.RecursoEducativo.Id_Recurso == recurso_id)
        .first()
    )
    if not recurso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El recurso educativo con ID {recurso_id} no existe",
        )

    return StandardResponse(
        success=True,
        data=RecursoOut.model_validate(recurso).model_dump(),
        message="Recurso educativo obtenido correctamente",
    )


@router.post("", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def crear_recurso(
    datos: RecursoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_staff),
):
    """
    Caso de Uso: GestionarRecursosEducativos.
    Crea un nuevo artículo asignando el Id_usuario del creador (Admin u Orientador).
    """
    nuevo_recurso = models.RecursoEducativo(
        Id_admin=current_user.Id_usuario,
        Titulo=datos.Titulo,
        Categoria=datos.Categoria,
        Contenido_markdown=datos.Contenido_markdown,
        Tiempo_lectura=datos.Tiempo_lectura,
    )
    db.add(nuevo_recurso)
    db.commit()
    db.refresh(nuevo_recurso)

    return StandardResponse(
        success=True,
        data=RecursoOut.model_validate(nuevo_recurso).model_dump(),
        message="Recurso educativo creado con éxito",
    )


@router.put(
    "/{recurso_id}",
    response_model=StandardResponse,
    dependencies=[Depends(require_staff)],
)
def actualizar_recurso(
    recurso_id: int,
    datos: RecursoUpdate,
    db: Session = Depends(get_db),
):
    """Actualiza el título, categoría, contenido Markdown o tiempo de lectura de un recurso."""
    recurso = (
        db.query(models.RecursoEducativo)
        .filter(models.RecursoEducativo.Id_Recurso == recurso_id)
        .first()
    )
    if not recurso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El recurso educativo con ID {recurso_id} no existe",
        )

    campos_actualizados = datos.model_dump(exclude_unset=True)
    for campo, valor in campos_actualizados.items():
        setattr(recurso, campo, valor)

    db.commit()
    db.refresh(recurso)

    return StandardResponse(
        success=True,
        data=RecursoOut.model_validate(recurso).model_dump(),
        message="Recurso educativo actualizado correctamente",
    )


@router.delete(
    "/{recurso_id}",
    response_model=StandardResponse,
    dependencies=[Depends(require_admin)],
)
def eliminar_recurso(recurso_id: int, db: Session = Depends(get_db)):
    """Elimina un recurso educativo de la biblioteca (Solo Admin)."""
    recurso = (
        db.query(models.RecursoEducativo)
        .filter(models.RecursoEducativo.Id_Recurso == recurso_id)
        .first()
    )
    if not recurso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El recurso educativo con ID {recurso_id} no existe",
        )

    db.delete(recurso)
    db.commit()

    return StandardResponse(
        success=True,
        data=None,
        message="Recurso educativo eliminado correctamente",
    )
