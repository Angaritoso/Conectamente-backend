
-- INICIALIZACIÓN DE LA BASE DE DATOS

CREATE DATABASE IF NOT EXISTS conectamente_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE conectamente_db; 

-- ENTIDADES PRINCIPALES Y CATÁLOGOS BASE

-- Usuario (Gestión de acceso y roles RBAC)

CREATE TABLE IF NOT EXISTS Usuario (
    Id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    Email VARCHAR(150) NOT NULL UNIQUE,
    Name VARCHAR(100) NOT NULL,
    Password_hash VARCHAR(250) NOT NULL,
    Rol ENUM('Estudiante', 'admin', 'orientador') NOT NULL DEFAULT 'Estudiante',
    Fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Estado BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

-- Emocion (Módulo 1: Conoce tus emociones)

CREATE TABLE IF NOT EXISTS Emocion (
    Id_emocion INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(50) NOT NULL UNIQUE,
    Descripcion TEXT NOT NULL,
    Estrategias_afrontamiento TEXT NULL,
    Icono_url VARCHAR(250) NULL
) ENGINE=InnoDB;

-- MÓDULOS DE CONTENIDO ADMINISTRABLE (ASOCIACIÓN 1 A 0..*)


-- Recurso_Educativo (Módulo 3: Biblioteca Aprende)

CREATE TABLE IF NOT EXISTS Recurso_Educativo (
    Id_Recurso INT AUTO_INCREMENT PRIMARY KEY,
    Id_admin INT NOT NULL,
    Titulo VARCHAR(200) NULL,
    Categoria VARCHAR(50) NOT NULL,
    Contenido_markdown TEXT NULL,
    Tiempo_lectura INT NULL,
    Fecha_publicacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_recurso_admin
        FOREIGN KEY (Id_admin) REFERENCES Usuario(Id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Red_Apoyo (Módulo 5: Directorio y Botón SOS)

CREATE TABLE IF NOT EXISTS Red_Apoyo (
    Id_red_Ap INT AUTO_INCREMENT PRIMARY KEY,
    Id_admin INT NOT NULL,
    Nombre_entidad VARCHAR(100) NOT NULL,
    Tipo_servicio VARCHAR(50) NOT NULL,
    Telefono VARCHAR(50) NOT NULL,
    Email_contacto VARCHAR(100) NULL,
    Horario_atencion VARCHAR(50) NOT NULL,
    Sitio_web VARCHAR(100) NULL,
    Es_linea_emergencia BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_red_apoyo_admin
        FOREIGN KEY (Id_admin) REFERENCES Usuario(Id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Actividades_interactivas (Módulo 4: Ejercicios guiados)

CREATE TABLE IF NOT EXISTS Actividades_interactivas (
    Id_actividades INT AUTO_INCREMENT PRIMARY KEY,
    Id_admin INT NOT NULL,
    Id_emocion INT NULL,
    Titulo VARCHAR(150) NOT NULL,
    Tipo_actividad VARCHAR(50) NOT NULL,
    Instrucciones TEXT NOT NULL,
    Duracion_estimada INT NOT NULL,
    CONSTRAINT fk_actividad_admin
        FOREIGN KEY (Id_admin) REFERENCES Usuario(Id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_actividad_emocion
        FOREIGN KEY (Id_emocion) REFERENCES Emocion(Id_emocion)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- PARTE 4: MÓDULO DEPENDIENTE POR COMPOSICIÓN (1 A 0..*)

-- Diario_Emocion_Usuario (Módulo 4: Bitácora privada del estudiante)
CREATE TABLE IF NOT EXISTS Diario_Emocion_Usuario (
    Id_diario_usuario INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    Id_emocion INT NOT NULL,
    Nota_priv TEXT NULL,
    Fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_diario_usuario
        FOREIGN KEY (id_usuario) REFERENCES Usuario(Id_usuario)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_diario_emocion
        FOREIGN KEY (Id_emocion) REFERENCES Emocion(Id_emocion)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- PARTE 5: REGISTROS ANÓNIMOS INDEPENDIENTES (FUERA DE LA ARQUITECTURA)

-- Encuesta_diagnostico (Fase 1: Diagnóstico anónimo)

CREATE TABLE IF NOT EXISTS Encuesta_diagnostico (
    Id_encuesta INT AUTO_INCREMENT PRIMARY KEY,
    Rango_edad VARCHAR(50) NOT NULL,
    Necesidad_principal VARCHAR(100) NOT NULL,
    Detalles TEXT NOT NULL,
    Fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Tabla: Feedback_usabilidad (Fases 4 y 5: Evaluación de usabilidad)
CREATE TABLE IF NOT EXISTS Feedback_usabilidad (
    Id_feedback INT AUTO_INCREMENT PRIMARY KEY,
    Calificacion_facilidad INT NOT NULL,
    Utilidad_percibida INT NOT NULL,
    Comentario_mejora TEXT NULL,
    Fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;