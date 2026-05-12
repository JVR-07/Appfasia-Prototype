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

### ✅ Arquitectura y diseño completados

- Stack tecnológico definido
- Contrato de API REST (19 endpoints, 6 módulos)
- Algoritmo diagnóstico Basal/Ceiling especificado
- Motor de inferencia BKT diseñado
- Pipeline de métricas clínicas (LME/IPF/TRA) definido
- Estrategia de contenido (315 recursos, 5 niveles)
- Entorno Docker Compose listo

### 🔜 Pendiente antes del primer sprint de código

| Prioridad | Área                                                |
| --------- | --------------------------------------------------- |
| 🔴 Alta   | Wireframes de pantallas (Modo Niño y Modo Padres)   |
| 🔴 Alta   | Seeding del grafo ArcadeDB (hitos y dependencias)   |
| 🟡 Media  | Sistema de diseño visual y avatar                   |
| 🟡 Media  | Algoritmo de repetición espaciada (detalle técnico) |
| 🟡 Media  | Biblioteca informativa para padres (artículos)      |
| 🟢 Baja   | Estrategia de testing                               |

---

## Licencia

Distribuido bajo la licencia **GNU General Public License v3.0**. Ver [`LICENSE`](./LICENSE) para más detalles.
