from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import (
    RedApoyoCreate,
    RedApoyoOut,
    RedApoyoUpdate,
    StandardResponse,
)
from app.security import require_admin

router = APIRouter(prefix="/red-apoyo", tags=["Módulo 5 - Red de Apoyo"])


@router.get("", response_model=StandardResponse)
def listar_red_apoyo(tipo_servicio: str | None = None, db: Session = Depends(get_db)):
    """
    Caso de Uso: ConsultarDirectivoApoyo.
    Retorna el directorio completo de instituciones y servicios de orientación disponibles.
    """
    query = db.query(models.RedApoyo)
    if tipo_servicio:
        query = query.filter(models.RedApoyo.Tipo_servicio.ilike(f"%{tipo_servicio}%"))

    contactos = query.order_by(
        models.RedApoyo.Es_linea_emergencia.desc(), models.RedApoyo.Nombre_entidad.asc()
    ).all()
    data = [RedApoyoOut.model_validate(c).model_dump() for c in contactos]

    return StandardResponse(
        success=True, data=data, message="Directorio de red de apoyo obtenido correctamente"
    )


@router.get("/emergencias", response_model=StandardResponse)
def listar_lineas_emergencia_sos(db: Session = Depends(get_db)):
    """
    Caso de Uso: ActivarBotonSOS.
    Acceso global público sin autenticación. Filtra únicamente las líneas de atención inmediata.
    """
    lineas_sos = (
        db.query(models.RedApoyo)
        .filter(models.RedApoyo.Es_linea_emergencia.is_(True))
        .order_by(models.RedApoyo.Nombre_entidad.asc())
        .all()
    )
    data = [RedApoyoOut.model_validate(c).model_dump() for c in lineas_sos]

    return StandardResponse(
        success=True, data=data, message="Líneas de emergencia SOS obtenidas con éxito"
    )


@router.get("/{red_id}", response_model=StandardResponse)
def obtener_contacto_red(red_id: int, db: Session = Depends(get_db)):
    """Obtiene los detalles de una entidad o línea de atención específica."""
    contacto = db.query(models.RedApoyo).filter(models.RedApoyo.Id_red_Ap == red_id).first()
    if not contacto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El contacto de red de apoyo con ID {red_id} no existe",
        )

    return StandardResponse(
        success=True,
        data=RedApoyoOut.model_validate(contacto).model_dump(),
        message="Contacto de red de apoyo obtenido correctamente",
    )


@router.post("", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def crear_contacto_red(
    datos: RedApoyoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_admin),
):
    """
    Caso de Uso: GestionContactosRedApoyo.
    Registra una nueva entidad o línea de ayuda en el directorio (Solo Admin).
    """
    nuevo_contacto = models.RedApoyo(
        Id_admin=current_user.Id_usuario,
        Nombre_entidad=datos.Nombre_entidad,
        Tipo_servicio=datos.Tipo_servicio,
        Telefono=datos.Telefono,
        Email_contacto=datos.Email_contacto,
        Horario_atencion=datos.Horario_atencion,
        Sitio_web=datos.Sitio_web,
        Es_linea_emergencia=datos.Es_linea_emergencia,
    )
    db.add(nuevo_contacto)
    db.commit()
    db.refresh(nuevo_contacto)

    return StandardResponse(
        success=True,
        data=RedApoyoOut.model_validate(nuevo_contacto).model_dump(),
        message="Contacto agregado exitosamente a la red de apoyo",
    )


@router.put("/{red_id}", response_model=StandardResponse)
def actualizar_contacto_red(
    red_id: int,
    datos: RedApoyoUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_admin),
):
    """Actualiza la información de una entidad o línea de la red de apoyo (Solo Admin)."""
    contacto = db.query(models.RedApoyo).filter(models.RedApoyo.Id_red_Ap == red_id).first()
    if not contacto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El contacto de red de apoyo con ID {red_id} no existe",
        )

    campos_actualizados = datos.model_dump(exclude_unset=True)
    for campo, valor in campos_actualizados.items():
        setattr(contacto, campo, valor)

    db.commit()
    db.refresh(contacto)

    return StandardResponse(
        success=True,
        data=RedApoyoOut.model_validate(contacto).model_dump(),
        message="Contacto de red de apoyo actualizado correctamente",
    )


@router.delete("/{red_id}", response_model=StandardResponse)
def eliminar_contacto_red(
    red_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_admin),
):
    """Elimina un contacto del directorio de red de apoyo (Solo Admin)."""
    contacto = db.query(models.RedApoyo).filter(models.RedApoyo.Id_red_Ap == red_id).first()
    if not contacto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El contacto de red de apoyo con ID {red_id} no existe",
        )

    db.delete(contacto)
    db.commit()

    return StandardResponse(
        success=True, data=None, message="Contacto eliminado correctamente de la red de apoyo"
    )
