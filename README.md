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

| Componente      | Tecnología              |
| --------------- | ----------------------- |
| Framework       | React + TypeScript      |
| Bundler         | Vite                    |
| Estado global   | Zustand                 |
| Animaciones     | Framer Motion           |
| Drag & Drop     | dnd-kit                 |
| TTS Avatar      | Web Speech API (nativa) |
| Audio/Micrófono | Web Audio API (nativa)  |

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
├── frontend/                  # App React + TypeScript (pendiente)
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

### 4. Verificar que el backend responde

```bash
curl http://localhost:8000/health
```

### 5. Interfaces de administración disponibles

| Servicio        | URL                        | Credenciales              |
| --------------- | -------------------------- | ------------------------- |
| API Swagger UI  | http://localhost:8000/docs | —                         |
| ArcadeDB Studio | http://localhost:2480      | `root` / valor del `.env` |

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

### ✅ Implementaciones Completadas (Sprints 1-4)

- **Arquitectura y Diseño:** Stack tecnológico, Contrato API, Algoritmo Diagnóstico Basal/Ceiling, Motor BKT, Pipeline de Métricas (LME/IPF/TRA) y Estrategia de contenido.
- **Backend (API y Motor):** API REST (FastAPI), Base de datos PostgreSQL inicializada, Autenticación JWT, Integración de servicios AI (Azure STT, Gemini LLM). Cobertura de QA con 124 tests de lógica clínica.
- **Base de Datos (Seeding):** Scripts de inicialización `seed_postgres.py` (palabras base) y `seed_arcadedb.py` (grafo de conocimiento).
- **Frontend (Sistema de Diseño):** Inicialización React + Vite + TS + Zustand. Sistema UI Vanilla CSS con enfoque lúdico, variables consistentes, animaciones suaves y componentes "Glassmorphism".
- **Modo Padres:** Vistas de Login y Dashboard responsivas. Implementación completa del componente Chatbot Asistente Flotante (animado con click-outside y auto-scroll).
- **Modo Niños:**
  - Mapa interactivo de progreso vertical (estilo Duolingo) con conexiones dinámicas SVG.
  - **Orquestador de Sesiones:** Motor funcional para ejecutar diagnósticos y lecciones.
  - **Ejercicios Interactivos:** Plantillas V-M (Naming), A-M (Repetition) y T-S (Match).
  - **Integración Nativa:** Uso de la Web Speech API (Reconocimiento de voz y Síntesis de voz) en los ejercicios, incluyendo mecanismos robustos de "fallback" de accesibilidad y pruebas simuladas.

### 🔜 Próximos Pasos (Sprint 5 y posteriores)

| Prioridad | Área                                                            |
| --------- | --------------------------------------------------------------- |
| 🔴 Alta   | Componente Avatar interactivo animado para guiar al niño        |
| 🔴 Alta   | Integración End-to-End: Conectar Frontend React con Backend API |
| 🟡 Media  | Lógica de renderizado y persistencia real de la ruta en la DB   |
| 🟡 Media  | Especificación e implementación de los 3 Minijuegos de refuerzo |
| 🟢 Baja   | Artículos reales para la biblioteca informativa RAG             |

---

## Licencia

Distribuido bajo la licencia **GNU General Public License v3.0**. Ver [`LICENSE`](./LICENSE) para más detalles.
