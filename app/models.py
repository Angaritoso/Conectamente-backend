from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Usuario(Base):
    __tablename__ = "Usuario"

    Id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    Email = Column(String(150), unique=True, nullable=False, index=True)
    Name = Column(String(100), nullable=False)
    Password_hash = Column(String(250), nullable=False)
    Rol = Column(
        Enum("Estudiante", "admin", "orientador", name="rol_usuario_enum"),
        nullable=False,
        default="Estudiante",
    )
    Fecha_registro = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    Estado = Column(Boolean, default=True, nullable=False)

    # Relaciones
    diario_entradas = relationship(
        "DiarioEmocionUsuario",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )
    recursos_creados = relationship(
        "RecursoEducativo",
        back_populates="autor",
    )
    actividades_creadas = relationship(
        "ActividadesInteractivas",
        back_populates="autor",
    )
    contactos_creados = relationship(
        "RedApoyo",
        back_populates="autor",
    )


class Emocion(Base):
    __tablename__ = "Emocion"

    Id_emocion = Column(Integer, primary_key=True, autoincrement=True)
    Nombre = Column(String(50), unique=True, nullable=False)
    Descripcion = Column(Text, nullable=False)
    Estrategias_afrontamiento = Column(Text, nullable=True)
    Icono_url = Column(String(250), nullable=True)

    # Relaciones
    diario_entradas = relationship(
        "DiarioEmocionUsuario",
        back_populates="emocion",
    )
    actividades = relationship(
        "ActividadesInteractivas",
        back_populates="emocion",
    )


class RecursoEducativo(Base):
    __tablename__ = "Recurso_Educativo"

    Id_Recurso = Column(Integer, primary_key=True, autoincrement=True)
    Id_admin = Column(
        Integer,
        ForeignKey("Usuario.Id_usuario"),
        nullable=False,
    )
    Titulo = Column(String(200), nullable=True)
    Categoria = Column(String(50), nullable=False, index=True)
    Contenido_markdown = Column(Text, nullable=True)
    Tiempo_lectura = Column(Integer, nullable=True, default=5)
    Fecha_publicacion = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    # Relaciones
    autor = relationship(
        "Usuario",
        back_populates="recursos_creados",
    )


class RedApoyo(Base):
    __tablename__ = "Red_Apoyo"

    Id_red_Ap = Column(Integer, primary_key=True, autoincrement=True)
    Id_admin = Column(
        Integer,
        ForeignKey("Usuario.Id_usuario"),
        nullable=False,
    )
    Nombre_entidad = Column(String(100), nullable=False)
    Tipo_servicio = Column(String(50), nullable=False)
    Telefono = Column(String(50), nullable=False)
    Email_contacto = Column(String(100), nullable=True)
    Horario_atencion = Column(String(50), nullable=False)
    Sitio_web = Column(String(100), nullable=True)
    Es_linea_emergencia = Column(Boolean, default=False, nullable=False, index=True)

    # Relaciones
    autor = relationship(
        "Usuario",
        back_populates="contactos_creados",
    )


class ActividadesInteractivas(Base):
    __tablename__ = "Actividades_interactivas"

    Id_actividades = Column(Integer, primary_key=True, autoincrement=True)
    Id_admin = Column(
        Integer,
        ForeignKey("Usuario.Id_usuario"),
        nullable=False,
    )
    Id_emocion = Column(
        Integer,
        ForeignKey("Emocion.Id_emocion"),
        nullable=True,
        index=True,
    )
    Titulo = Column(String(150), nullable=False)
    Tipo_actividad = Column(String(50), nullable=False)
    Instrucciones = Column(Text, nullable=False)
    Duracion_estimada = Column(Integer, nullable=False)

    # Relaciones
    autor = relationship(
        "Usuario",
        back_populates="actividades_creadas",
    )
    emocion = relationship(
        "Emocion",
        back_populates="actividades",
    )


class DiarioEmocionUsuario(Base):
    __tablename__ = "Diario_Emocion_Usuario"

    Id_diario_usuario = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(
        Integer,
        ForeignKey("Usuario.Id_usuario", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    Id_emocion = Column(
        Integer,
        ForeignKey("Emocion.Id_emocion"),
        nullable=False,
    )
    Nota_priv = Column(Text, nullable=True)
    Fecha_registro = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    # Relaciones
    usuario = relationship(
        "Usuario",
        back_populates="diario_entradas",
    )
    emocion = relationship(
        "Emocion",
        back_populates="diario_entradas",
    )


class EncuestaDiagnostico(Base):
    __tablename__ = "Encuesta_diagnostico"

    Id_encuesta = Column(Integer, primary_key=True, autoincrement=True)
    Rango_edad = Column(String(50), nullable=False)
    Necesidad_principal = Column(String(100), nullable=False)
    Detalles = Column(Text, nullable=False)
    Fecha_creacion = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )


class FeedbackUsabilidad(Base):
    __tablename__ = "Feedback_usabilidad"

    Id_feedback = Column(Integer, primary_key=True, autoincrement=True)
    Calificacion_facilidad = Column(Integer, nullable=False)
    Utilidad_percibida = Column(Integer, nullable=False)
    Comentario_mejora = Column(Text, nullable=True)
    Fecha_creacion = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
