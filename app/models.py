from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(Enum("estudiante", "admin", "orientador", name="roles_enum"), nullable=False, default="estudiante")
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    estado = Column(Boolean, default=True, nullable=False)

    # Relaciones
    diario_entradas = relationship("DiarioEmocionUsuario", back_populates="usuario", cascade="all, delete-orphan")
    recursos_creados = relationship
    (
        "RecursoEducativo", 
        back_populates="autor")
    actividades_creadas = relationship
    (
        "ActividadInteractiva", 
        back_populates="autor"
        )
    contactos_creados = relationship
    (
        "RedApoyo", 
        back_populates="autor"
        )


class Emocion(Base):
    __tablename__ = "emociones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(Text, nullable=False)
    estrategias_afrontamiento = Column(Text, nullable=True)
    icono_url = Column(String(255), nullable=True)

    # Relaciones
    diario_entradas = relationship("DiarioEmocionUsuario", back_populates="emocion")
    actividades = relationship("ActividadInteractiva", back_populates="emocion")


class RecursoEducativo(Base):
    __tablename__ = "recursos_educativos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    titulo = Column(String(200), nullable=False)
    categoria = Column(String(50), nullable=False)
    contenido_markdown = Column(Text, nullable=False)
    tiempo_lectura = Column(Integer, default=5)
    fecha_publicacion = Column(DateTime, default=datetime.utcnow, nullable=False)

    autor = relationship("Usuario", back_populates="recursos_creados")


class ActividadInteractiva(Base):
    __tablename__ = "actividades_interactivas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    emocion_id = Column(Integer, ForeignKey("emociones.id"), nullable=True)
    titulo = Column(String(150), nullable=False)
    tipo_actividad = Column(String(50), nullable=False)
    instrucciones = Column(Text, nullable=False)
    duracion_estimada = Column(Integer, nullable=False)

    autor = relationship("Usuario", back_populates="actividades_creadas")
    emocion = relationship("Emocion", back_populates="actividades")


class DiarioEmocionUsuario(Base):
    __tablename__ = "diario_emociones_usuario"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    emocion_id = Column(Integer, ForeignKey("emociones.id"), nullable=False)
    nota_privada = Column(Text, nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)

    usuario = relationship("Usuario", back_populates="diario_entradas")
    emocion = relationship("Emocion", back_populates="diario_entradas")


class RedApoyo(Base):
    __tablename__ = "redes_apoyo"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nombre_entidad = Column(String(100), nullable=False)
    tipo_servicio = Column(String(50), nullable=False)
    telefono = Column(String(50), nullable=False)
    email_contacto = Column(String(100), nullable=True)
    horario_atencion = Column(String(50), nullable=False)
    sitio_web = Column(String(100), nullable=True)
    es_linea_emergencia = Column(Boolean, default=False, nullable=False)

    autor = relationship("Usuario", back_populates="contactos_creados")


# --- TABLAS AISLADAS POR PRIVACIDAD (REGISTROS ANÓNIMOS) ---

class EncuestaDiagnostico(Base):
    __tablename__ = "encuestas_diagnostico"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rango_edad = Column(String(50), nullable=False)
    necesidad_principal = Column(String(100), nullable=False)
    detalles = Column(Text, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)


class FeedbackUsabilidad(Base):
    __tablename__ = "feedback_usabilidad"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    calificacion_facilidad = Column(Integer, nullable=False)
    utilidad_percibida = Column(Integer, nullable=False)
    comentario_mejora = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)