CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Tutores (padres/cuidadores)
CREATE TABLE tutores (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre        VARCHAR(100) NOT NULL,
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Perfiles de niños
CREATE TABLE children (
    id_child         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_tutor         UUID NOT NULL REFERENCES tutores(id) ON DELETE CASCADE,
    nombre           VARCHAR(100) NOT NULL,
    fecha_nac        DATE NOT NULL,
    nivel_actual     SMALLINT DEFAULT NULL,
    diagnostico_ok   BOOLEAN DEFAULT FALSE,
    racha_dias       INT DEFAULT 0,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_children_tutor ON children(id_tutor);

-- Categorías de recursos
CREATE TABLE categorias (
    id      SERIAL PRIMARY KEY,
    nombre  VARCHAR(50) UNIQUE NOT NULL
);

-- Recursos léxicos (diccionario atómico)
CREATE TABLE recursos (
    id_recurso      VARCHAR(10) PRIMARY KEY,
    tipo            VARCHAR(20) NOT NULL,
    texto           TEXT NOT NULL,
    nivel_sugerido  SMALLINT NOT NULL,
    fonema_objetivo VARCHAR(10),
    id_categoria    INT REFERENCES categorias(id),
    dificultad_art  VARCHAR(10),
    imagen_url      TEXT,
    audio_url       TEXT,
    tags            TEXT[],
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_recursos_nivel     ON recursos(nivel_sugerido);
CREATE INDEX idx_recursos_fonema    ON recursos(fonema_objetivo);
CREATE INDEX idx_recursos_tags      ON recursos USING GIN(tags);
CREATE INDEX idx_recursos_categoria ON recursos(id_categoria);

-- Maestría de hitos por niño (estado BKT permanente)
CREATE TABLE hito_mastery (
    id_child     UUID NOT NULL REFERENCES children(id_child) ON DELETE CASCADE,
    id_hito      VARCHAR(20) NOT NULL,
    p_mastery    FLOAT NOT NULL DEFAULT 0.0,
    is_mastered  BOOLEAN DEFAULT FALSE,
    updated_at   TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id_child, id_hito)
);
CREATE INDEX idx_hito_mastery_child ON hito_mastery(id_child);

-- Diagnósticos completados
CREATE TABLE diagnosticos (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_child            UUID NOT NULL REFERENCES children(id_child) ON DELETE CASCADE,
    nivel_detectado     SMALLINT NOT NULL,
    total_interacciones SMALLINT NOT NULL,
    razon_finalizacion  VARCHAR(20) NOT NULL,
    historial_json      JSONB,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_diagnosticos_child ON diagnosticos(id_child);

-- Sesiones de ejercicios
CREATE TABLE sesiones (
    id_sesion              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_child               UUID NOT NULL REFERENCES children(id_child) ON DELETE CASCADE,
    fecha_inicio           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_fin              TIMESTAMPTZ,
    nivel_sesion           SMALLINT NOT NULL,
    estado                 VARCHAR(20) DEFAULT 'EN_CURSO',
    etiqueta_tutor         VARCHAR(20),
    r0_weight              FLOAT DEFAULT 0.5,
    ejercicios_completados SMALLINT DEFAULT 0,
    ipf_promedio           FLOAT,
    hitos_dominados_hoy    SMALLINT DEFAULT 0
);
CREATE INDEX idx_sesiones_child ON sesiones(id_child);
CREATE INDEX idx_sesiones_fecha ON sesiones(fecha_inicio DESC);

-- Resultados por ejercicio
CREATE TABLE resultados_ejercicio (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_sesion     UUID NOT NULL REFERENCES sesiones(id_sesion) ON DELETE CASCADE,
    id_recurso    VARCHAR(10) REFERENCES recursos(id_recurso),
    id_hito       VARCHAR(20),
    plantilla     VARCHAR(30),
    hardware_req  VARCHAR(5),
    lme           FLOAT,
    ipf           FLOAT,
    tra_ms        INT,
    es_correcto   BOOLEAN,
    intentos      SMALLINT DEFAULT 1,
    es_minijuego  BOOLEAN DEFAULT FALSE,
    es_timeout    BOOLEAN DEFAULT FALSE,
    timestamp_res TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_resultados_sesion ON resultados_ejercicio(id_sesion);

-- Refresh tokens
CREATE TABLE refresh_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_tutor    UUID NOT NULL REFERENCES tutores(id) ON DELETE CASCADE,
    token_hash  TEXT NOT NULL,
    expires_at  TIMESTAMPTZ NOT NULL,
    revoked     BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_refresh_tokens_tutor ON refresh_tokens(id_tutor);

-- Categorías base
INSERT INTO categorias (nombre) VALUES
    ('animales'), ('alimentos'), ('partes_del_cuerpo'), ('familia'),
    ('objetos_del_hogar'), ('juguetes'), ('ropa'), ('colores_y_formas'),
    ('verbos'), ('emociones'), ('naturaleza_y_ciencia'), ('profesiones'),
    ('lugares'), ('lenguaje_figurado'), ('transporte'), ('conceptos_abstractos');

-- Publicaciones
CREATE TABLE publicaciones (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo      VARCHAR(200) NOT NULL,
    resumen     TEXT NOT NULL,
    contenido   TEXT,
    tags        TEXT[] DEFAULT '{}',
    imagen_url  TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_pub_created ON publicaciones(created_at DESC);

-- Seed de publicaciones iniciales
INSERT INTO publicaciones (titulo, resumen, tags) VALUES
    ('Bienvenido a Appfasia', 'Tu asistente inteligente para el apoyo en terapia del lenguaje.', ARRAY['bienvenida']),
    ('¿Qué son los fonemas?', 'Un fonema es la unidad mínima de sonido que puede distinguir significados.', ARRAY['educación', 'fonología']),
    ('Consejos para practicar en casa', 'Actividades sencillas que puedes hacer con tu pequeño fuera de la aplicación.', ARRAY['consejos', 'práctica']);

