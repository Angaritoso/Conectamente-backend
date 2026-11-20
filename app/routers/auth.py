from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import (
    RolEnum,
    StandardResponse,
    TokenResponse,
    UsuarioCreate,
    UsuarioLogin,
    UsuarioOut,
    UsuarioRoleUpdate,
    UsuarioUpdate,
)
from app.security import (
    create_access_token,
    get_password_hash,
    require_admin,
    require_authenticated,
    verify_password,
)

router = APIRouter(tags=["Autenticación y Usuarios"])


# SECCIÓN A: AUTENTICACIÓN PÚBLICA Y REGISTRO (/auth)


@router.post("/auth/register", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def registrar_estudiante(datos: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registra una nueva cuenta de usuario con el rol predeterminado 'Estudiante'.
    Verifica la restricción Unique del atributo Email definida en el diagrama de clases.
    """
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.Email == datos.Email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya se encuentra registrado en la plataforma",
        )

    nuevo_usuario = models.Usuario(
        Email=datos.Email,
        Name=datos.Name,
        Password_hash=get_password_hash(datos.Password),
        Rol=RolEnum.estudiante.value,
        Estado=True,
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return StandardResponse(
        success=True,
        data=UsuarioOut.model_validate(nuevo_usuario).model_dump(),
        message="Usuario registrado exitosamente",
    )


@router.post("/auth/login", response_model=StandardResponse)
def iniciar_sesion(credenciales: UsuarioLogin, db: Session = Depends(get_db)):
    """
    Caso de Uso: IniciarSesion (Estudiante, Administrador y Orientador).
    Verifica credenciales contra Password_hash y retorna el token JWT firmado.
    """
    usuario = db.query(models.Usuario).filter(models.Usuario.Email == credenciales.Email).first()
    if not usuario or not verify_password(credenciales.Password, usuario.Password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.Estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta se encuentra inactiva. Contacta al administrador.",
        )

    access_token = create_access_token(
        data={
            "sub": str(usuario.Id_usuario),
            "email": usuario.Email,
            "rol": usuario.Rol,
        }
    )

    respuesta_token = TokenResponse(
        access_token=access_token,
        user=UsuarioOut.model_validate(usuario),
    )

    return StandardResponse(
        success=True, data=respuesta_token.model_dump(), message="Inicio de sesión exitoso"
    )


# SECCIÓN B: GESTIÓN DE PERFIL PROPIO (/auth/me)


@router.get("/auth/me", response_model=StandardResponse)
def obtener_mi_perfil(current_user: models.Usuario = Depends(require_authenticated)):
    """
    Caso de Uso: GestionarPerfil.
    Retorna los datos del perfil del usuario autenticado (Estudiante, Admin u Orientador).
    """
    return StandardResponse(
        success=True,
        data=UsuarioOut.model_validate(current_user).model_dump(),
        message="Perfil de usuario obtenido correctamente",
    )


@router.put("/auth/me", response_model=StandardResponse)
def actualizar_mi_perfil(
    datos: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_authenticated),
):
    """
    Caso de Uso: GestionarPerfil.
    Permite al usuario autenticado actualizar su nombre, correo electrónico o contraseña.
    """
    if datos.Email and datos.Email != current_user.Email:
        email_en_uso = db.query(models.Usuario).filter(models.Usuario.Email == datos.Email).first()
        if email_en_uso:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nuevo correo electrónico ya está siendo utilizado por otra cuenta",
            )
        current_user.Email = datos.Email

    if datos.Name is not None:
        current_user.Name = datos.Name

    if datos.Password is not None:
        current_user.Password_hash = get_password_hash(datos.Password)

    db.commit()
    db.refresh(current_user)

    return StandardResponse(
        success=True,
        data=UsuarioOut.model_validate(current_user).model_dump(),
        message="Perfil actualizado correctamente",
    )


# SECCIÓN C: ADMINISTRACIÓN DE USUARIOS Y ROLES (/admin/users)


@router.get("/admin/users", response_model=StandardResponse)
def listar_usuarios(
    rol: RolEnum | None = None,
    activo: bool | None = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_admin),
):
    """Lista todas las cuentas de usuario registradas con filtros opcionales (Solo Admin)."""
    query = db.query(models.Usuario)

    if rol is not None:
        query = query.filter(models.Usuario.Rol == rol.value)
    if activo is not None:
        query = query.filter(models.Usuario.Estado == activo)

    usuarios = query.order_by(models.Usuario.Fecha_registro.desc()).all()
    data = [UsuarioOut.model_validate(u).model_dump() for u in usuarios]

    return StandardResponse(
        success=True, data=data, message="Lista de usuarios obtenida correctamente"
    )


@router.post("/admin/users", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario_por_admin(
    datos: UsuarioCreate,
    rol: RolEnum = RolEnum.estudiante,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_admin),
):
    """
    Caso de Uso: RegistrarUsuario (Actor: Administrador).
    Permite al administrador registrar cuentas institucionales asignando directamente el rol.
    """
    existente = db.query(models.Usuario).filter(models.Usuario.Email == datos.Email).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado",
        )

    nuevo_usuario = models.Usuario(
        Email=datos.Email,
        Name=datos.Name,
        Password_hash=get_password_hash(datos.Password),
        Rol=rol.value,
        Estado=True,
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return StandardResponse(
        success=True,
        data=UsuarioOut.model_validate(nuevo_usuario).model_dump(),
        message=f"Usuario creado exitosamente con el rol '{rol.value}'",
    )


@router.put("/admin/users/{usuario_id}/role", response_model=StandardResponse)
def cambiar_rol_o_estado_usuario(
    usuario_id: int,
    datos: UsuarioRoleUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_admin),
):
    """Modifica el rol ('Estudiante', 'admin', 'orientador') o el estado activo de un usuario (Solo Admin)."""
    usuario = db.query(models.Usuario).filter(models.Usuario.Id_usuario == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El usuario con ID {usuario_id} no existe",
        )

    usuario.Rol = datos.Rol.value
    if datos.Estado is not None:
        usuario.Estado = datos.Estado

    db.commit()
    db.refresh(usuario)

    return StandardResponse(
        success=True,
        data=UsuarioOut.model_validate(usuario).model_dump(),
        message="Permisos y estado del usuario actualizados correctamente",
    )
