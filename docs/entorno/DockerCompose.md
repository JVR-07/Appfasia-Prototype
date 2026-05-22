# Entorno de Desarrollo — Docker Compose

> Appfasia Prototype · Versión 0.2

---

## 1. Servicios del Stack Local

| Servicio              | Imagen                       | Puerto local                 | Descripción                                  |
| --------------------- | ---------------------------- | ---------------------------- | -------------------------------------------- |
| **PostgreSQL**        | `postgres:16-alpine`         | `5432`                       | BD principal — recursos, usuarios, sesiones  |
| **ArcadeDB**          | `arcadedata/arcadedb:latest` | `2480` (HTTP), `7687` (BOLT) | Grafo de conocimiento — hitos y dependencias |
| **Redis**             | `redis:7-alpine`             | `6379`                       | Caché de sesión y estado BKT                 |
| **Backend (FastAPI)** | Build local                  | `8000`                       | API REST + Motor de Inferencia               |
| **Frontend (React)**  | Build local                  | `5173` (HTTPS)               | SPA interactiva para Modo Niño y Modo Padres |

> Los servicios externos (Azure Blob Storage, Azure Speech Service, Gemini API) son cloud y **no requieren Docker**.

---

## 2. Estructura de Directorios del Proyecto

```
appfasia-prototype/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                    # Punto de entrada FastAPI
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── children.py
│   │   │   ├── diagnostic.py
│   │   │   ├── session.py
│   │   │   ├── progress.py
│   │   │   └── chatbot.py
│   │   └── deps.py                # Dependencias JWT, DB connections
│   ├── inference_engine/
│   │   ├── bkt/
│   │   ├── rules/
│   │   ├── graph/
│   │   ├── decision/
│   │   ├── memory/
│   │   └── diagnostic/
│   ├── services/
│   │   ├── azure_speech.py        # Azure STT
│   │   ├── azure_blob.py          # Azure Blob Storage
│   │   ├── gemini.py              # LLM Avatar/Chatbot
│   │   └── metrics.py             # LME, IPF, TRA
│   └── models/
│       └── schemas.py             # Modelos Pydantic
├── frontend/                      # React + Vite + TypeScript (SPA)
│   ├── src/
│   │   ├── components/            # Componentes reutilizables (Ejercicios, Chatbot)
│   │   ├── pages/                 # Vistas (ChildPath, DiagnosticExam, ParentDashboard)
│   │   ├── store/                 # Estado global con Zustand
│   │   └── services/              # Clientes de API REST
│   ├── package.json
│   ├── vite.config.ts             # Configuración de Vite con SSL (HTTPS) y Proxy
│   └── Dockerfile                 # Contenedor para levantar el frontend en desarrollo
├── scripts/
│   ├── seed_content.py            # Importación CSV → PostgreSQL + Azure Blob
│   ├── seed_postgres.py           # Ingesta inicial de datos en PostgreSQL
│   ├── seed_graph.py              # Ingesta inicial del grafo en ArcadeDB
│   ├── generate_audios.py         # Batch Azure TTS → MP3
│   └── upload_assets.py           # Subida masiva a Azure Blob Storage
├── docker/
│   └── postgres/
│       └── init.sql               # Esquema inicial de la BD
├── content/
│   ├── seed_resources.csv         # Catálogo maestro de recursos
│   └── imagenes/                  # Imágenes locales antes de subir a Azure
├── docker-compose.yml
├── .env                           # Variables de entorno (NO subir a git)
├── .env.example                   # Plantilla pública de variables
└── .gitignore
```

---

## 3. `docker-compose.yml`

```yaml
version: "3.9"

services:
  # ──────────────────────────────────────────────
  # PostgreSQL — Base de datos relacional principal
  # ──────────────────────────────────────────────
  postgres:
    image: postgres:16-alpine
    container_name: appfasia_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ──────────────────────────────────────────────
  # ArcadeDB — Grafo de conocimiento (hitos BKT)
  # ──────────────────────────────────────────────
  arcadedb:
    image: arcadedata/arcadedb:latest
    container_name: appfasia_arcadedb
    restart: unless-stopped
    environment:
      ARCADEDB_SERVER_ROOTPASSWORD: ${ARCADEDB_ROOT_PASSWORD}
    ports:
      - "2480:2480" # HTTP REST / Studio UI
      - "7687:7687" # BOLT (compatible con driver neo4j)
    volumes:
      - arcadedb_data:/home/arcadedb/databases
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:2480/api/v1/ready"]
      interval: 15s
      timeout: 10s
      retries: 5
      start_period: 30s

  # ──────────────────────────────────────────────
  # Redis — Caché de sesión y estado BKT
  # ──────────────────────────────────────────────
  redis:
    image: redis:7-alpine
    container_name: appfasia_redis
    restart: unless-stopped
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD}
      --appendonly yes
      --appendfsync everysec
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ──────────────────────────────────────────────
  # Backend FastAPI — Motor de Inferencia + API
  # ──────────────────────────────────────────────
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: appfasia_backend
    restart: unless-stopped
    env_file: .env
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app # Hot-reload: cambios en código se reflejan al instante
    depends_on:
      postgres:
        condition: service_healthy
      arcadedb:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: >
      sh -c "
      python scripts/seed_postgres.py &&
      python scripts/seed_graph.py --bolt=$$ARCADEDB_BOLT --user=$$ARCADEDB_USER --password=$$ARCADEDB_ROOT_PASSWORD --database=$$ARCADEDB_DATABASE &&
      uvicorn main:app --host 0.0.0.0 --port 8000 --reload
      "

  # ──────────────────────────────────────────────
  # Frontend React — Interfaz Web
  # ──────────────────────────────────────────────
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: appfasia_frontend
    restart: unless-stopped
    environment:
      - CI=true
      - PNPM_CONFIG_FROZEN_LOCKFILE=false
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

volumes:
  postgres_data:
  arcadedb_data:
  redis_data:

networks:
  default:
    name: appfasia_network
```

---

## 4. `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema (necesarias para algunas librerías)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Descargar modelo de spaCy en español
RUN python -m spacy download es_core_news_sm

# Copiar código (en dev esto es sobreescrito por el volumen)
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 5. `backend/requirements.txt`

```txt
# ── Core API ──────────────────────────────────────
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic[email]==2.8.2
python-dotenv==1.0.1
httpx==0.27.2

# ── Autenticación JWT ─────────────────────────────
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# ── Base de datos relacional ──────────────────────
asyncpg==0.29.0          # Driver async PostgreSQL

# ── Grafo de conocimiento (ArcadeDB vía BOLT) ────
neo4j==5.23.1            # Compatible con ArcadeDB por protocolo BOLT
networkx==3.3            # Para tests y simulaciones offline

# ── Caché ─────────────────────────────────────────
redis[hiredis]==5.0.8

# ── Motor de Inferencia ───────────────────────────
pyBKT==1.4.1
numpy==1.26.4
pandas==2.2.2

# ── NLP y métricas clínicas ───────────────────────
spacy==3.7.5             # es_core_news_sm para LME
editex==0.3.0            # Distancia fonética para IPF

# ── Azure (STT + Blob Storage) ────────────────────
azure-cognitiveservices-speech==1.40.0
azure-storage-blob==12.22.0
azure-identity==1.17.1

# ── LLM Avatar / Chatbot ──────────────────────────
google-generativeai==0.8.3   # Gemini 2.5 Flash
```

---

## 6. `.env.example`

Copiar a `.env` y rellenar los valores reales. **Nunca subir `.env` al repositorio.**

```bash
# ── PostgreSQL ────────────────────────────────────
POSTGRES_DB=appfasia
POSTGRES_USER=appfasia_user
POSTGRES_PASSWORD=CHANGE_ME_strong_password
DATABASE_URL=postgresql+asyncpg://appfasia_user:CHANGE_ME_strong_password@postgres:5432/appfasia

# ── ArcadeDB ──────────────────────────────────────
ARCADEDB_ROOT_PASSWORD=CHANGE_ME_arcadedb_password
ARCADEDB_URL=bolt://arcadedb:7687
ARCADEDB_USER=root
ARCADEDB_DATABASE=appfasia_graph

# ── Redis ─────────────────────────────────────────
REDIS_PASSWORD=CHANGE_ME_redis_password
REDIS_URL=redis://:CHANGE_ME_redis_password@redis:6379/0

# ── JWT ───────────────────────────────────────────
JWT_SECRET_KEY=CHANGE_ME_generate_with_openssl_rand_hex_32
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# ── Azure Speech Service (STT) ────────────────────
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_SPEECH_REGION=eastus

# ── Azure Blob Storage ────────────────────────────
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_STORAGE_CONTAINER=appfasia-assets
AZURE_CDN_BASE_URL=https://appfasia.azureedge.net

# ── Gemini LLM ────────────────────────────────────
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_PRIMARY_MODEL=gemini-2.5-flash
GEMINI_FALLBACK_MODEL=gemini-2.5-flash-lite

# ── Entorno ───────────────────────────────────────
ENVIRONMENT=development    # development | production
DEBUG=true
```

---

## 7. `docker/postgres/init.sql`

Este script se ejecuta automáticamente la primera vez que se levanta el contenedor de PostgreSQL.

```sql
-- Extensión para UUIDs
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Tabla de Tutores (padres/cuidadores)
CREATE TABLE tutores (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre      VARCHAR(100) NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de Usuarios (niños)
CREATE TABLE usuarios (
    id_usuario      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre          VARCHAR(100) NOT NULL,
    fecha_nac       DATE NOT NULL,
    id_tutor        UUID NOT NULL REFERENCES tutores(id) ON DELETE CASCADE,
    nivel_actual    SMALLINT,           -- NULL hasta completar diagnóstico
    p_l0_inicial    FLOAT,              -- Resultado del diagnóstico
    racha_dias      INT DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_usuarios_tutor ON usuarios(id_tutor);

-- Tabla de Categorías
CREATE TABLE categorias (
    id      SERIAL PRIMARY KEY,
    nombre  VARCHAR(50) UNIQUE NOT NULL
);

-- Tabla de Recursos (Diccionario Atómico)
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
CREATE INDEX idx_recursos_nivel    ON recursos(nivel_sugerido);
CREATE INDEX idx_recursos_fonema   ON recursos(fonema_objetivo);
CREATE INDEX idx_recursos_dificultad ON recursos(dificultad_art);
CREATE INDEX idx_recursos_tags     ON recursos USING GIN(tags);
CREATE INDEX idx_recursos_categoria ON recursos(id_categoria);

-- Tabla de Diagnósticos
CREATE TABLE diagnosticos (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id              UUID NOT NULL REFERENCES usuarios(id_usuario),
    nivel_detectado       SMALLINT NOT NULL,
    p_l0_inicial          FLOAT NOT NULL,
    total_interacciones   SMALLINT NOT NULL,
    razon_finalizacion    VARCHAR(20) NOT NULL,
    historial_json        JSONB,
    created_at            TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_diagnosticos_child ON diagnosticos(child_id);

-- Tabla de Sesiones
CREATE TABLE sesiones (
    id_sesion       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_usuario      UUID NOT NULL REFERENCES usuarios(id_usuario),
    fecha_inicio    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fecha_fin       TIMESTAMPTZ,
    nivel_sesion    SMALLINT NOT NULL,
    estado          VARCHAR(20) DEFAULT 'EN_CURSO',
    etiqueta_tutor  VARCHAR(20),
    r0_weight       FLOAT DEFAULT 0.5,
    ejercicios_completados SMALLINT DEFAULT 0,
    ipf_promedio    FLOAT,
    payload_json    JSONB
);
CREATE INDEX idx_sesiones_usuario ON sesiones(id_usuario);
CREATE INDEX idx_sesiones_fecha   ON sesiones(fecha_inicio DESC);

-- Tabla de Resultados por Ejercicio
CREATE TABLE resultados_ejercicio (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_sesion       UUID NOT NULL REFERENCES sesiones(id_sesion),
    id_recurso      VARCHAR(10) REFERENCES recursos(id_recurso),
    plantilla       VARCHAR(30),
    hardware_req    VARCHAR(5),
    lme             FLOAT,
    ipf             FLOAT,
    tra_ms          INT,
    es_correcto     BOOLEAN,
    intentos        SMALLINT DEFAULT 1,
    es_minijuego    BOOLEAN DEFAULT FALSE,
    es_timeout      BOOLEAN DEFAULT FALSE,
    timestamp_res   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_resultados_sesion  ON resultados_ejercicio(id_sesion);
CREATE INDEX idx_resultados_recurso ON resultados_ejercicio(id_recurso);

-- Insertar categorías base
INSERT INTO categorias (nombre) VALUES
    ('animales'), ('alimentos'), ('partes_del_cuerpo'), ('familia'),
    ('objetos_del_hogar'), ('juguetes'), ('ropa'), ('colores_y_formas'),
    ('verbos'), ('emociones'), ('naturaleza_y_ciencia'), ('profesiones'),
    ('lugares'), ('lenguaje_figurado'), ('transporte'), ('conceptos_abstractos');
```

---

## 8. `.gitignore`

```gitignore
# Variables de entorno
.env

# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/

# Node / Frontend
node_modules/
dist/
.eslintcache
*.log

# Contenido local
content/imagenes/
content/audios/

# IDEs
.vscode/
.idea/
*.swp
```

---

## 9. Comandos de Gestión del Entorno

### Primera vez (setup completo)

```bash
# 1. Clonar el repositorio y entrar al directorio
git clone <repo_url> && cd appfasia-prototype

# 2. Copiar y configurar variables de entorno
cp .env.example .env
# → Editar .env con las claves reales de Azure y Gemini

# 3. Generar un JWT_SECRET_KEY seguro
openssl rand -hex 32

# 4. Levantar todos los servicios (seeding automático de Postgres y ArcadeDB incluido)
docker compose up -d

# 5. Verificar que todos los servicios están saludables
docker compose ps
```

---

### Acceso a interfaces de administración y aplicaciones

| Servicio               | URL                                                      | Credenciales                      |
| ---------------------- | -------------------------------------------------------- | --------------------------------- |
| **Frontend App**       | [https://localhost:5173](https://localhost:5173)         | Cuenta de Tutor registrada        |
| **FastAPI Swagger UI** | [http://localhost:8000/docs](http://localhost:8000/docs) | —                                 |
| **ArcadeDB Studio**    | [http://localhost:2480](http://localhost:2480)           | `root` / `ARCADEDB_ROOT_PASSWORD` |
| **PostgreSQL**         | `localhost:5432`                                         | Variables del `.env`              |
| **Redis**              | `localhost:6379`                                         | `REDIS_PASSWORD` del `.env`       |

---

### 🎙️ Configuración de Seguridad e Ingesta de Audio (Desarrollo)

- **Certificado SSL de Vite:** El frontend se expone a través de HTTPS con `basicSsl` para cumplir con las políticas estrictas del navegador para capturar el micrófono. Al abrir [https://localhost:5173](https://localhost:5173), haz clic en **Avanzado → Proceder / Continuar** para aceptar el certificado de desarrollo.
- **Navegador recomendado:** Utiliza **Google Chrome oficial**.
- **Limitación de Brave / Chromium:** Al usar Brave u otros navegadores libres en Linux/Arch, la Web Speech API nativa falla inmediatamente con `Speech recognition error network` por motivos de privacidad (Brave bloquea la conexión de envío de voz a Google Cloud). En estos casos, puedes utilizar los botones de **"Escribir"** o **"Simular Éxito"** para avanzar en las lecciones sin que se te penalice por errores técnicos.

---

### Seeding de contenido (Manual)

Si necesitas forzar el seeding del catálogo o de los archivos multimedia manualmente:

```bash
# Generar audios con Azure TTS (requiere .env configurado con llave)
docker compose exec backend python scripts/generate_audios.py

# Subir imágenes y audios a Azure Blob Storage
docker compose exec backend python scripts/upload_assets.py

# Importar CSV a PostgreSQL
docker compose exec backend python scripts/seed_content.py \
  --csv content/seed_resources.csv \
  --phase 0      # 0 = Solo Nivel 1 (MVP), 1-3 = fases completas
```

---

## 10. Verificación de Salud del Stack

```bash
# Verificar que el frontend responde (ignorar advertencia de certificado)
curl -k https://localhost:5173

# Verificar que FastAPI responde
curl http://localhost:8000/health

# Verificar PostgreSQL
docker compose exec postgres pg_isready -U appfasia_user

# Verificar ArcadeDB
curl http://localhost:2480/api/v1/ready

# Verificar Redis
docker compose exec redis redis-cli -a $REDIS_PASSWORD ping
# → Debe responder: PONG
```
