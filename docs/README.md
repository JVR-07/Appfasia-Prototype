# Documentación Técnica de Appfasia

> Índice maestro · Última actualización: Mayo 2026

Este documento es el punto de entrada a toda la documentación técnica del proyecto. Navega por las secciones según el área de interés.

---

## Documentos de Referencia

### 📋 Planificación

| Documento                                              | Descripción                                                                                                 |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| [PlanificacionProyecto.md](./PlanificacionProyecto.md) | Plan completo del proyecto: objetivos, módulos, métricas clínicas, hitos de aprendizaje y lógica adaptativa |

---

### 🏗️ Arquitectura del Sistema

Ubicación: `docs/arquitectura/`

| Documento                                                         | Descripción                                                                                                                                                                                                       |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [ArquitecturaTecnica.md](./arquitectura/ArquitecturaTecnica.md)   | Stack tecnológico, capa de datos (PostgreSQL + ArcadeDB + Redis + Azure Blob), motor de inferencia BKT, métricas clínicas (LME/IPF/TRA), motor de contenido, integración del Avatar con LLM y frontend adaptativo |
| [ContratoAPI.md](./arquitectura/ContratoAPI.md)                   | Contrato completo de la API REST: 19 endpoints en 6 módulos (Auth, Children, Diagnostic, Session, Progress, Chatbot) con request/response bodies                                                                  |
| [AlgoritmoDiagnostico.md](./arquitectura/AlgoritmoDiagnostico.md) | Especificación técnica del algoritmo Basal/Ceiling: máquina de estados, lógica de progresión, cálculo de P(L0) para el BKT y casos borde                                                                          |

---

### 📦 Contenido y Recursos

Ubicación: `docs/contenido/`

| Documento                                                    | Descripción                                                                                                                                                                                                           |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [EstrategiaContenido.md](./contenido/EstrategiaContenido.md) | Catálogo de 315 recursos distribuidos en 5 niveles y 16 categorías semánticas, estrategia de imágenes (Flaticon/Freepik), generación de audios con Azure TTS, estructura del CSV de seeding y pipeline de importación |
| [BibliotecaPadres.md](./contenido/BibliotecaPadres.md)       | Catálogo de artículos informativos para el Modo Padres: 13 artículos en 4 categorías, estructura JSON por artículo, estrategia de almacenamiento y base de conocimiento RAG para el chatbot                           |

---

### ⚙️ Backend (Motor)

Ubicación: `docs/backend/`

| Documento                                          | Descripción                                                                                                                                                                                                   |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [MotorInferencia.md](./backend/MotorInferencia.md) | Documentación oficial de la implementación del BKT, métricas (IPF/LME/TRA/SEM), plantillas de ejercicio, evaluador semántico LLM, dosificación, reglas clínicas, ~200 hitos y máquina de estados diagnóstica. |

---

### 🖥️ Frontend

Ubicación: `docs/frontend/`

| Documento                                 | Descripción                                                                                                                                  |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| [Wireframes.md](./frontend/Wireframes.md) | Estructura de las 20 pantallas de la app (13 Modo Niño + 7 Modo Padres) con plantilla por completar: componentes, estados, navegación y APIs |

---

### 🐳 Entorno de Desarrollo

Ubicación: `docs/entorno/`

| Documento                                      | Descripción                                                                                                                                                             |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [DockerCompose.md](./entorno/DockerCompose.md) | Configuración completa del entorno local: `docker-compose.yml`, `Dockerfile` del backend, `requirements.txt`, `.env.example`, esquema SQL inicial y comandos de gestión |
| [Testing.md](./entorno/Testing.md)             | Estrategia de QA para el motor y frontend, cubriendo `pytest`, uso de mocks (`fakeredis`, `unittest.mock`) y detalle de los 124 tests de la capa clínica del Sprint 1.  |

---

## Estado de la Documentación

### ✅ Completado

| Área                                 | Documento                  |
| ------------------------------------ | -------------------------- |
| Stack tecnológico y framework        | ArquitecturaTecnica.md     |
| Capa de datos híbrida                | ArquitecturaTecnica.md     |
| Motor de inferencia BKT              | ArquitecturaTecnica.md     |
| Pipeline de métricas clínicas        | ArquitecturaTecnica.md     |
| Motor de contenido y plantillas      | ArquitecturaTecnica.md     |
| Integración Avatar + LLM             | ArquitecturaTecnica.md     |
| Frontend adaptativo (especificación) | ArquitecturaTecnica.md     |
| Contrato de API REST (19 endpoints)  | ContratoAPI.md             |
| Autenticación JWT                    | ContratoAPI.md             |
| Algoritmo Diagnóstico Basal/Ceiling  | AlgoritmoDiagnostico.md    |
| Estrategia de contenido (315 items)  | EstrategiaContenido.md     |
| Entorno Docker Compose               | DockerCompose.md           |
| Estructura de wireframes             | frontend/Wireframes.md     |
| Lógica Clínica e Implementación BKT  | backend/MotorInferencia.md |
| Plantillas de Ejercicio (8 tipos)    | backend/MotorInferencia.md |
| Evaluador Semántico LLM (SEM)        | backend/MotorInferencia.md |
| Alcance de Hitos (~200 nodos)        | backend/MotorInferencia.md |
| Estrategia de QA y Suite de Pruebas  | entorno/Testing.md         |
| Seeding del grafo ArcadeDB           | entorno/DockerCompose.md   |
| Importación del catálogo a Postgres  | entorno/DockerCompose.md   |
| Integración End-to-End Front/Back    | ArquitecturaTecnica.md     |
| Inicialización y Config. de Frontend | README principal           |
| Sistema de Diseño e UI (Modo Padres) | frontend/Wireframes.md     |
| Orquestador y Ejercicios (Modo Niño) | frontend/Wireframes.md     |

---

### 🔜 Pendientes — Bloque 1 · Frontend y Conexión

| Área                                                   | Documento destino      | Prioridad |
| ------------------------------------------------------ | ---------------------- | --------- |
| Diseño visual del Avatar (nombre, estilo, animaciones) | frontend/Wireframes.md | 🔴 Alta   |
| Especificación de Minijuegos (mecánicas de juego)      | frontend/Wireframes.md | 🟡 Media  |
