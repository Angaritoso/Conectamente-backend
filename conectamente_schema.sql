
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

-- PARTE 6: ÍNDICES DE RENDIMIENTO PARA CONSULTAS FRECUENTES

CREATE INDEX idx_recurso_categoria ON Recurso_Educativo(Categoria);
CREATE INDEX idx_red_apoyo_sos ON Red_Apoyo(Es_linea_emergencia);
CREATE INDEX idx_diario_usuario_fecha ON Diario_Emocion_Usuario(id_usuario, Fecha_registro);
CREATE INDEX idx_actividades_emocion ON Actividades_interactivas(Id_emocion);

-- PARTE 7: DATOS SEMILLA (SEED DATA)

-- 7.1 Usuario Administrador Base (Requerido como FK Id_admin para cargar contenidos)
INSERT IGNORE INTO Usuario (Email, Name, Password_hash, Rol, Estado)
VALUES (
    'admin@conectamente.edu.co',
    'Administrador ConectaMente',
    '$2b$12$DwmJm1k79Zr6gVnq4VdmeOK3PogRfxXYQ2z74tlHpNIVg/6tHtGE2',  
    'admin',
    TRUE
);

-- Captura del Id_usuario del administrador para las llaves foráneas
SET @id_admin_base = (
    SELECT Id_usuario
    FROM Usuario
    WHERE Email = 'admin@conectamente.edu.co'
    LIMIT 1
);

-- 7.2 Módulo 1: Catálogo de las 6 Emociones Primarias
INSERT IGNORE INTO Emocion (Nombre, Descripcion, Estrategias_afrontamiento, Icono_url) VALUES
(
    'Alegría',
    'Estado emocional de bienestar, satisfacción y entusiasmo que surge ante logros, vínculos positivos o experiencias gratificantes.',
    'Comparte el momento con personas de confianza; registra qué generó este estado en tu diario emocional para reconocer tus fuentes de bienestar; practica la gratitud consciente.',
    '/assets/icons/emociones/alegria.svg'
),
(
    'Tristeza',
    'Respuesta natural ante pérdidas, decepciones o situaciones dolorosas que invita a la pausa, la introspección y la búsqueda de contención.',
    'Permítete sentir y expresar la emoción sin juzgarte; escribe lo que sientes en tu diario privado; conversa con un amigo, familiar u orientador; evita el aislamiento prolongado.',
    '/assets/icons/emociones/tristeza.svg'
),
(
    'Miedo',
    'Mecanismo de alerta que se activa frente a una amenaza real o percibida, preparando al cuerpo para protegerse ante la incertidumbre.',
    'Practica respiración diafragmática lenta (inhalar en 4 tiempos, sostener 4, exhalar en 6); diferencia entre hechos reales y pensamientos anticipatorios; divide el reto en pasos pequeños y manejables.',
    '/assets/icons/emociones/miedo.svg'
),
(
    'Enojo',
    'Emoción intensa que aparece cuando percibimos injusticia, vulneración de límites personales o bloqueo de metas importantes.',
    'Haz una pausa física antes de responder (regla de los 10 minutos); libera tensión con respiración profunda o caminata breve; expresa tu inconformidad usando comunicación asertiva sin agresión.',
    '/assets/icons/emociones/enojo.svg'
),
(
    'Frustración',
    'Sensación de impotencia o malestar que surge cuando los resultados no coinciden con el esfuerzo realizado o aparecen obstáculos imprevistos.',
    'Reevalúa las expectativas y ajusta el plan por metas alcanzables; identifica qué factores están bajo tu control y cuáles no; pide retroalimentación a un docente o compañero.',
    '/assets/icons/emociones/frustracion.svg'
),
(
    'Preocupación',
    'Estado de inquietud mental enfocado en problemas futuros o exigencias académicas y sociales que puede derivar en sobrecarga si se mantiene.',
    'Anota tus pendientes por orden de prioridad y asigna horarios realistas; desconéctate de pantallas antes de dormir; enfoca tu atención en una sola tarea a la vez.',
    '/assets/icons/emociones/preocupacion.svg'
);

-- 7.3 Módulo 5: Contactos Iniciales de Red de Apoyo y Botón SOS (Colombia)
INSERT INTO Red_Apoyo (
    Id_admin,
    Nombre_entidad,
    Tipo_servicio,
    Telefono,
    Email_contacto,
    Horario_atencion,
    Sitio_web,
    Es_linea_emergencia
) VALUES
(
    @id_admin_base,
    'Línea 106 - Apoyo Psicosocial y Salud Mental',
    'Atención Psicosocial',
    '106',
    NULL,
    '24 horas / 7 días',
    NULL,
    TRUE
),
(
    @id_admin_base,
    'Línea 123 - Emergencias Nacionales',
    'Emergencia General',
    '123',
    NULL,
    '24 horas / 7 días',
    NULL,
    TRUE
),
(
    @id_admin_base,
    'Línea 192 (Opción 4) - Ministerio de Salud',
    'Orientación en Salud Mental',
    '192 (Opción 4)',
    NULL,
    '24 horas / 7 días',
    'https://www.minsalud.gov.co',
    TRUE
),
(
    @id_admin_base,
    'Línea 141 - ICBF Protección a Niños y Jóvenes',
    'Protección Juvenil',
    '141',
    NULL,
    '24 horas / 7 días',
    'https://www.icbf.gov.co',
    TRUE
),
(
    @id_admin_base,
    'Orientación Escolar / Bienestar Institucional',
    'Orientación Educativa',
    'Consultar extensión institucional',
    'orientacion@institucion.edu.co',
    'Lunes a Viernes 7:00 AM - 4:00 PM',
    NULL,
    FALSE
);