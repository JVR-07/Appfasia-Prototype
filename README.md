<div align="center">

# Appfasia

**Plataforma adaptativa e inteligente para el apoyo en trastornos del aprendizaje del lenguaje**

[![Estado](https://img.shields.io/badge/estado-prototipo-orange)](.)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](.)
[![FastAPI](https://img.shields.io/badge/framework-FastAPI-009688)](.)
[![React](https://img.shields.io/badge/frontend-React+TypeScript-61DAFB)](.)
[![License](https://img.shields.io/badge/licencia-GPL%20v3-blue)](./LICENSE)

</div>

---

## ¿Qué es Appfasia?

Appfasia es una plataforma web/móvil basada en inteligencia artificial que actúa como asistente educativo interactivo para niños con trastornos del lenguaje (afasia y disfasia). La plataforma se divide en dos modos:

- **Modo Niño:** Un personaje virtual ("amigo imaginario") guía al niño a través de ejercicios de lenguaje adaptados a su nivel real de competencia, detectado mediante un diagnóstico inicial basado en el algoritmo Basal/Ceiling.
- **Modo Padres:** Panel de seguimiento con métricas traducidas a lenguaje no técnico, historial de sesiones, chatbot asistente con IA y biblioteca informativa sobre afasia y disfasia.

> ⚠️ **Proyecto en fase de prototipo.** No está destinado a producción ni uso clínico formal.

---

## Características principales

- 🧠 **Motor de inferencia híbrido:** Combina IA simbólica (reglas clínicas) con IA probabilística (Bayesian Knowledge Tracing) para personalizar el aprendizaje.
- 🎯 **Evaluación diagnóstica adaptativa:** Algoritmo Basal/Ceiling que detecta el nivel real del niño en ≤ 15 interacciones.
- 📊 **Métricas clínicas:** LME (Longitud Media del Enunciado), IPF (Índice de Precisión Fonológica) y TRA (Tasa de Respuesta Auditiva).
- 🔁 **Repetición espaciada:** Revisiones programadas a 24h, 3d, 7d y 21d para consolidar hitos dominados.
- 🎮 **Gamificación:** Tres minijuegos integrados como refuerzo positivo (Rescate del Avatar, Cazador de Burbujas, Memorama Auditivo).
- 💬 **Avatar con LLM:** Personaje virtual potenciado por Gemini 2.5 Flash que adapta su comunicación al estado emocional y de aprendizaje del niño.
- 📱 **Dosificación automática:** Límites de sesión basados en las recomendaciones de la AAP según rango de edad.

---

## Stack Tecnológico

### Backend

| Componente               | Tecnología                                |
| ------------------------ | ----------------------------------------- |
| Framework API            | FastAPI (Python 3.11+)                    |
| Base de datos relacional | PostgreSQL 16                             |
| Grafo de conocimiento    | ArcadeDB (Cypher/BOLT)                    |
| Caché de sesión          | Redis 7                                   |
| Motor BKT                | pyBKT + NumPy                             |
| NLP / LME                | spaCy (es_core_news_sm)                   |
| Fonología / IPF          | editex                                    |
| STT                      | Azure Speech Service (F0 — 5h/mes gratis) |
| LLM Avatar               | Gemini 2.5 Flash / Flash-Lite             |
| Almacenamiento           | Azure Blob Storage + CDN                  |

### Frontend

| Componente      | Tecnología                             |
| --------------- | -------------------------------------- |
| Framework       | React + TypeScript                     |
| Bundler         | Vite + basicSsl (HTTPS)                |
| Estado global   | Zustand                                |
| Animaciones     | Framer Motion                          |
| Drag & Drop     | dnd-kit                                |
| TTS Avatar      | Web Speech API (Sintetizador nativo)   |
| Audio/Micrófono | Web Speech API (Reconocimiento nativo) |

---

## Estructura del Repositorio

```
appfasia-prototype/
├── backend/                   # API FastAPI + Motor de Inferencia
│   ├── main.py
│   ├── api/v1/                # Endpoints (auth, children, diagnostic, session…)
│   ├── inference_engine/      # BKT, reglas, grafo, decisión, memoria
│   ├── services/              # Azure STT, Azure Blob, Gemini LLM
│   └── models/                # Schemas Pydantic
├── frontend/                  # App React + TypeScript (Vite)
│   ├── src/
│   │   ├── components/        # Componentes UI de ejercicios y chatbot
│   │   ├── pages/             # Vistas de Modo Niño y Modo Padres
│   │   ├── store/             # Zustand stores para estado global
│   │   └── services/          # Clientes API
│   └── vite.config.ts         # Configuración con soporte de Proxy e HTTPS
├── scripts/                   # Seeding de contenido y assets
│   ├── seed_content.py
│   ├── generate_audios.py
│   └── upload_assets.py
├── content/
│   └── seed_resources.csv     # Catálogo maestro de 315 recursos
├── docker/
│   └── postgres/init.sql      # Esquema inicial de PostgreSQL
├── docs/                      # Documentación técnica completa
│   └── README.md              # Índice de toda la documentación
├── docker-compose.yml
├── .env.example
└── README.md                  ← Este archivo
```

---

## Inicio Rápido (Entorno de Desarrollo)

### Requisitos previos

- Docker + Docker Compose
- Credenciales de **Azure** (Speech Service + Blob Storage)
- API Key de **Google Gemini**

### 1. Clonar y configurar variables de entorno

```bash
git clone <repo_url>
cd appfasia-prototype

cp .env.example .env
# Editar .env con las claves reales de Azure y Gemini
```

### 2. Generar el JWT Secret

```bash
openssl rand -hex 32
# Pegar el resultado en JWT_SECRET_KEY del .env
```

### 3. Levantar el stack completo

```bash
docker compose up -d

# Verificar que todos los servicios están saludables
docker compose ps
```

> 💡 **Seeding Automático:** Al levantar el stack por primera vez, el contenedor de backend ejecutará automáticamente los scripts `seed_postgres.py` y `seed_graph.py` para poblar PostgreSQL y ArcadeDB respectivamente.

### 4. Interfaces y Aplicaciones disponibles

| Servicio            | URL / Puerto                                             | Credenciales                                         |
| ------------------- | -------------------------------------------------------- | ---------------------------------------------------- |
| **Frontend Web**    | [https://localhost:5173](https://localhost:5173)         | Cuenta registrada de Tutor                           |
| **API Swagger UI**  | [http://localhost:8000/docs](http://localhost:8000/docs) | —                                                    |
| **ArcadeDB Studio** | [http://localhost:2480](http://localhost:2480)           | `root` / valor de `ARCADEDB_ROOT_PASSWORD` en `.env` |
| **PostgreSQL**      | `localhost:5432`                                         | Credenciales de `POSTGRES_USER` en `.env`            |
| **Redis**           | `localhost:6379`                                         | Clave de `REDIS_PASSWORD` en `.env`                  |

---

## 🎙️ Nota Importante sobre el Micrófono (Desarrollo)

El reconocimiento de voz del frontend (`webkitSpeechRecognition`) utiliza la API nativa del navegador. Por motivos de seguridad de los navegadores, **el micrófono solo funciona bajo contextos seguros (HTTPS o localhost)**.

1. **Aceptar Certificado Auto-firmado:** Al ingresar por primera vez a [https://localhost:5173](https://localhost:5173), tu navegador mostrará una advertencia de seguridad. Haz clic en **Avanzado → Continuar de todos modos**. Esto es necesario para habilitar las APIs seguras.
2. **Navegadores Soportados:** Se recomienda utilizar **Google Chrome oficial**.
3. **Brave Browser / Chromium en Linux:** Brave y las variantes libres de Chromium deshabilitan por defecto el soporte de Web Speech API para proteger la privacidad (ya que Chromium envía el audio a transcribir a los servidores de Google y no procesa localmente). Si experimentas un `Speech recognition error network` en estos navegadores:
   - **Brave/Chromium:** Utiliza los botones de rescate **"⌨️ Escribir"** o **"✨ Simular Éxito"** provistos en el cuadro de alerta de error del ejercicio.
   - **Firefox:** Habilita el reconocimiento en `about:config` poniendo en `true` las variables `media.webspeech.recognition.enable` y `media.webspeech.recognition.force_enable`.

---

## Documentación

Toda la documentación técnica se encuentra en [`/docs`](./docs/README.md).

| Área                     | Documento                                                              |
| ------------------------ | ---------------------------------------------------------------------- |
| Arquitectura del sistema | [ArquitecturaTecnica.md](./docs/arquitectura/ArquitecturaTecnica.md)   |
| Contrato de API REST     | [ContratoAPI.md](./docs/arquitectura/ContratoAPI.md)                   |
| Algoritmo diagnóstico    | [AlgoritmoDiagnostico.md](./docs/arquitectura/AlgoritmoDiagnostico.md) |
| Estrategia de contenido  | [EstrategiaContenido.md](./docs/contenido/EstrategiaContenido.md)      |
| Entorno Docker Compose   | [DockerCompose.md](./docs/entorno/DockerCompose.md)                    |
| Wireframes Frontend      | [Wireframes.md](./docs/frontend/Wireframes.md)                         |

---

## Estado del Proyecto

### ✅ Implementaciones Completadas

- **Arquitectura y Capa de Datos:** Stack multi-base de datos, Contrato API, Algoritmo Diagnóstico Basal/Ceiling, Motor BKT, Pipeline de Métricas (LME/IPF/TRA) y Estrategia de contenido.
- **Backend (API y Motor):** API REST (FastAPI), Base de datos PostgreSQL inicializada, Autenticación JWT, Integración de servicios AI (Azure STT, Gemini LLM). Cobertura de QA con 124 tests de lógica clínica.
- **Base de Datos (Seeding):** Ingesta y asociación automatizada en `docker-compose` de `seed_postgres.py` y `seed_graph.py` (grafo de hitos).
- **Frontend y Diseño Lúdico:** Inicialización React + Vite + TS + Zustand. Sistema UI Vanilla CSS con enfoque lúdico, variables de color consistentes y componentes con estilo "Glassmorphism".
- **Modo Padres:** Vistas de Registro/Login, Dashboard de progreso y chatbot asistente contextual animado.
- **Modo Niños:**
  - Mapa interactivo de progreso vertical (estilo Duolingo) con conexiones dinámicas SVG y carga de progreso en tiempo real desde la BD.
  - **Orquestador de Sesiones:** Orquestación funcional end-to-end de los exámenes de diagnóstico y las lecciones periódicas adaptadas con el backend.
  - **Ejercicios Interactivos:** Plantillas funcionales para Naming (V-M), Repetition (A-M), Match (T-S), Constructor (T-A) e Historias (Narrator/Thinker).
  - **Gestión de Errores de Voz:** Mitigación inteligente de problemas con el micrófono (red, bloqueos o silencio) sin penalizar el progreso adaptativo del niño, integrando flujos de fallback ("Escribir" / "Simular Éxito").
  - **Corrección en Identificador:** Resuelto el fallo sistemático de comprobación incorrecta en los ejercicios tipo `match` (Identificador) garantizando el mapeo correcto de `idRecurso`.

### 🔜 Funcionalidades fuera de este prototipo

| Prioridad | Área                                                            |
| --------- | --------------------------------------------------------------- |
| 🔴 Alta   | Componente Avatar interactivo animado para guiar al niño        |
| 🟡 Media  | Especificación e implementación de los 3 Minijuegos de refuerzo |
| 🟢 Baja   | Artículos reales para la biblioteca informativa RAG             |

---

## Licencia

Distribuido bajo la licencia **GNU General Public License v3.0**. Ver [`LICENSE`](./LICENSE) para más detalles.
