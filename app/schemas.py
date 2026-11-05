from datetime import datetime
from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, AliasChoices


# Estructuras estandar de respuesta con (API REST)

class ErrorDetail(BaseModel):
    code: str = Field(..., examples=["VALIDATION_ERROR"])
    details: str = Field(..., examples=["Descripción detallada del error"])


class StandardResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    message: str = "Operación realizada con éxito"


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


# Modulo 0: Autenticacion y usuarios
# Tabla: Usuario

class RolEnum(str, Enum):
    estudiante = "Estudiante"
    admin = "admin"
    orientador = "orientador"


class UsuarioBase(BaseModel):
    Email: EmailStr = Field(
        ...,
        max_length=150,
        validation_alias=AliasChoices("Email", "email"),
        examples=["estudiante@colegio.edu.co"]
    )
    Name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        validation_alias=AliasChoices("Name", "name", "nombre"),
        examples=["Carlos Ramírez"]
    )


class UsuarioCreate(UsuarioBase):
    Password: str = Field(
        ...,
        min_length=6,
        max_length=50,
        validation_alias=AliasChoices("Password", "password")
    )


class UsuarioUpdate(BaseModel):
    Name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        validation_alias=AliasChoices("Name", "name", "nombre")
    )
    Email: Optional[EmailStr] = Field(
        None,
        max_length=150,
        validation_alias=AliasChoices("Email", "email")
    )
    Password: Optional[str] = Field(
        None,
        min_length=6,
        max_length=50,
        validation_alias=AliasChoices("Password", "password")
    )


class UsuarioRoleUpdate(BaseModel):
    Rol: RolEnum = Field(..., validation_alias=AliasChoices("Rol", "rol"))
    Estado: Optional[bool] = Field(None, validation_alias=AliasChoices("Estado", "estado"))


class UsuarioLogin(BaseModel):
    Email: EmailStr = Field(..., validation_alias=AliasChoices("Email", "email"))
    Password: str = Field(..., validation_alias=AliasChoices("Password", "password"))


class UsuarioOut(BaseModel):
    Id_usuario: int
    Email: EmailStr
    Name: str
    Rol: RolEnum
    Fecha_registro: datetime
    Estado: bool

    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    rol: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UsuarioOut


# Modulo 1: Conoce tus emociones
# Tabla: Emocion

class EmocionBase(BaseModel):
    Nombre: str = Field(
        ...,
        max_length=50,
        validation_alias=AliasChoices("Nombre", "nombre")
    )
    Descripcion: str = Field(
        ...,
        validation_alias=AliasChoices("Descripcion", "descripcion")
    )
    Estrategias_afrontamiento: Optional[str] = Field(
        None,
        validation_alias=AliasChoices("Estrategias_afrontamiento", "estrategias_afrontamiento")
    )
    Icono_url: Optional[str] = Field(
        None,
        max_length=250,
        validation_alias=AliasChoices("Icono_url", "icono_url")
    )


class EmocionCreate(EmocionBase):
    pass


class EmocionUpdate(BaseModel):
    Descripcion: Optional[str] = Field(
        None,
        validation_alias=AliasChoices("Descripcion", "descripcion")
    )
    Estrategias_afrontamiento: Optional[str] = Field(
        None,
        validation_alias=AliasChoices("Estrategias_afrontamiento", "estrategias_afrontamiento")
    )
    Icono_url: Optional[str] = Field(
        None,
        max_length=250,
        validation_alias=AliasChoices("Icono_url", "icono_url")
    )


class EmocionOut(EmocionBase):
    Id_emocion: int

    model_config = ConfigDict(from_attributes=True)


# Modulo 2: Mi bienestar - Autorreflexion en memoria 
# esta no tiene tabla en BD

class DimensionBienestarEnum(str, Enum):
    estado_animo = "Estado de ánimo"
    estres_academico = "Estrés académico"
    relaciones_interpersonales = "Relaciones interpersonales"
    habitos_descanso = "Hábitos de descanso"
    apoyo_social = "Sensación de apoyo social"

# Escalas de 1 a 5
# Etiquetas de dos opciones

class PreguntaReflexionOut(BaseModel):
    pregunta_id: int
    dimension: DimensionBienestarEnum
    enunciado: str
    escala_min: int = 1
    escala_max: int = 5
    etiqueta_min: str = "Nunca / Muy bajo"
    etiqueta_max: str = "Siempre / Muy alto"


class ItemRespuestaReflexion(BaseModel):
    pregunta_id: int = Field(..., ge=1, le=10)
    valor: int = Field(
        ...,
        ge=1,
        le=5,
        description="Escala de 1 a 5 donde mayor puntaje representa mayor carga o alerta en la dimensión evaluada"
    )


class EvaluacionIn(BaseModel):
    respuestas: List[ItemRespuestaReflexion] = Field(..., min_length=1)


class ResultadoDimensionOut(BaseModel):
    dimension: str
    promedio: float
    estado: str
    observacion: str

# Se requiere que la aplicacion no pase por encima de diagnosticos medicos reales, se pone AVISO
class EvaluacionFeedbackOut(BaseModel):
    nivel_general: str
    puntaje_promedio: float
    aviso_etico: str = (
        "Este resultado es únicamente un ejercicio de autorreflexión educativa "
        "y no constituye un diagnóstico psicológico ni clínico."
    )
    desglose_dimensiones: List[ResultadoDimensionOut]
    recomendaciones: List[str]
    sugerir_red_apoyo: bool = False


# Modulo 3: Biblioteca aprende 
# Tabla: Recurso_Educativo

class RecursoBase(BaseModel):
    Titulo: str = Field(
        ...,
        max_length=200,
        validation_alias=AliasChoices("Titulo", "titulo")
    )
    Categoria: str = Field(
        ...,
        max_length=50,
        validation_alias=AliasChoices("Categoria", "categoria")
    )
    Contenido_markdown: str = Field(
        ...,
        validation_alias=AliasChoices("Contenido_markdown", "contenido_markdown")
    )
    Tiempo_lectura: Optional[int] = Field(
        5,
        ge=1,
        validation_alias=AliasChoices("Tiempo_lectura", "tiempo_lectura")
    )


class RecursoCreate(RecursoBase):
    pass


class RecursoUpdate(BaseModel):
    Titulo: Optional[str] = Field(None, max_length=200, validation_alias=AliasChoices("Titulo", "titulo"))
    Categoria: Optional[str] = Field(None, max_length=50, validation_alias=AliasChoices("Categoria", "categoria"))
    Contenido_markdown: Optional[str] = Field(
        None,
        validation_alias=AliasChoices("Contenido_markdown", "contenido_markdown")
    )
    Tiempo_lectura: Optional[int] = Field(
        None,
        ge=1,
        validation_alias=AliasChoices("Tiempo_lectura", "tiempo_lectura")
    )


class RecursoOut(RecursoBase):
    Id_Recurso: int
    Id_admin: int
    Fecha_publicacion: datetime

    model_config = ConfigDict(from_attributes=True)


# Modulo 4: Actividades e interaccion 
# Tablas: Actividades_interactivas y Diario_Emocion_Usuario

class ActividadBase(BaseModel):
    Titulo: str = Field(
        ...,
        max_length=150,
        validation_alias=AliasChoices("Titulo", "titulo")
    )
    Tipo_actividad: str = Field(
        ...,
        max_length=50,
        validation_alias=AliasChoices("Tipo_actividad", "tipo_actividad")
    )
    Instrucciones: str = Field(
        ...,
        validation_alias=AliasChoices("Instrucciones", "instrucciones")
    )
    Duracion_estimada: int = Field(
        ...,
        ge=1,
        validation_alias=AliasChoices("Duracion_estimada", "duracion_estimada")
    )
    Id_emocion: Optional[int] = Field(
        None,
        validation_alias=AliasChoices("Id_emocion", "id_emocion", "emocion_id")
    )


class ActividadCreate(ActividadBase):
    pass


class ActividadUpdate(BaseModel):
    Titulo: Optional[str] = Field(None, max_length=150, validation_alias=AliasChoices("Titulo", "titulo"))
    Tipo_actividad: Optional[str] = Field(
        None,
        max_length=50,
        validation_alias=AliasChoices("Tipo_actividad", "tipo_actividad")
    )
    Instrucciones: Optional[str] = Field(None, validation_alias=AliasChoices("Instrucciones", "instrucciones"))
    Duracion_estimada: Optional[int] = Field(
        None,
        ge=1,
        validation_alias=AliasChoices("Duracion_estimada", "duracion_estimada")
    )
    Id_emocion: Optional[int] = Field(
        None,
        validation_alias=AliasChoices("Id_emocion", "id_emocion", "emocion_id")
    )


class ActividadOut(ActividadBase):
    Id_actividades: int
    Id_admin: int

    model_config = ConfigDict(from_attributes=True)


class DiarioCreate(BaseModel):
    Id_emocion: int = Field(
        ...,
        validation_alias=AliasChoices("Id_emocion", "id_emocion", "emocion_id")
    )
    Nota_priv: Optional[str] = Field(
        None,
        validation_alias=AliasChoices("Nota_priv", "nota_priv", "nota_privada")
    )


class DiarioOut(BaseModel):
    Id_diario_usuario: int
    id_usuario: int
    Id_emocion: int
    Nota_priv: Optional[str] = None
    Fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)


# Modulo 5: Red de apoyo y boton SOS 
# Tabla: Red_Apoyo
class RedApoyoBase(BaseModel):
    Nombre_entidad: str = Field(
        ...,
        max_length=100,
        validation_alias=AliasChoices("Nombre_entidad", "nombre_entidad")
    )
    Tipo_servicio: str = Field(
        ...,
        max_length=50,
        validation_alias=AliasChoices("Tipo_servicio", "tipo_servicio")
    )
    Telefono: str = Field(
        ...,
        max_length=50,
        validation_alias=AliasChoices("Telefono", "telefono")
    )
    Email_contacto: Optional[EmailStr] = Field(
        None,
        max_length=100,
        validation_alias=AliasChoices("Email_contacto", "email_contacto")
    )
    Horario_atencion: str = Field(
        ...,
        max_length=50,
        validation_alias=AliasChoices("Horario_atencion", "horario_atencion")
    )
    Sitio_web: Optional[str] = Field(
        None,
        max_length=100,
        validation_alias=AliasChoices("Sitio_web", "sitio_web")
    )
    Es_linea_emergencia: bool = Field(
        False,
        validation_alias=AliasChoices("Es_linea_emergencia", "es_linea_emergencia")
    )


class RedApoyoCreate(RedApoyoBase):
    pass


class RedApoyoUpdate(BaseModel):
    Nombre_entidad: Optional[str] = Field(None, max_length=100, validation_alias=AliasChoices("Nombre_entidad", "nombre_entidad"))
    
    Tipo_servicio: Optional[str] = Field(None, max_length=50, validation_alias=AliasChoices("Tipo_servicio", "tipo_servicio"))
    
    Telefono: Optional[str] = Field(None, max_length=50, validation_alias=AliasChoices("Telefono", "telefono"))
    
    Email_contacto: Optional[EmailStr] = Field(None, max_length=100, validation_alias=AliasChoices("Email_contacto", "email_contacto"))
    
    Horario_atencion: Optional[str] = Field(None, max_length=50, validation_alias=AliasChoices("Horario_atencion", "horario_atencion"))
    
    Sitio_web: Optional[str] = Field(None, max_length=100, validation_alias=AliasChoices("Sitio_web", "sitio_web"))
    
    Es_linea_emergencia: Optional[bool] = Field(None, validation_alias=AliasChoices("Es_linea_emergencia", "es_linea_emergencia"))


class RedApoyoOut(RedApoyoBase):
    Id_red_Ap: int
    Id_admin: int

    model_config = ConfigDict(from_attributes=True)


# Tablas anonimas independientes  
# Encuesta_diagnostico y Feedback_usabilidad

class EncuestaDiagnosticoCreate(BaseModel):
    Rango_edad: str = Field(
        ...,
        max_length=50,
        validation_alias=AliasChoices("Rango_edad", "rango_edad")
    )
    Necesidad_principal: str = Field(
        ...,
        max_length=100,
        validation_alias=AliasChoices("Necesidad_principal", "necesidad_principal")
    )
    Detalles: str = Field(
        ...,
        validation_alias=AliasChoices("Detalles", "detalles")
    )


class EncuestaDiagnosticoOut(EncuestaDiagnosticoCreate):
    Id_encuesta: int
    Fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedbackUsabilidadCreate(BaseModel):
    Calificacion_facilidad: int = Field(
        ...,
        ge=1,
        le=5,
        validation_alias=AliasChoices("Calificacion_facilidad", "calificacion_facilidad")
    )
    Utilidad_percibida: int = Field(
        ...,
        ge=1,
        le=5,
        validation_alias=AliasChoices("Utilidad_percibida", "utilidad_percibida")
    )
    Comentario_mejora: Optional[str] = Field(
        None,
        validation_alias=AliasChoices("Comentario_mejora", "comentario_mejora")
    )


class FeedbackUsabilidadOut(FeedbackUsabilidadCreate):
    Id_feedback: int
    Fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)