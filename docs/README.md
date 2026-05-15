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

| Documento                                          | Descripción                                                                                                                                 |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| [MotorInferencia.md](./backend/MotorInferencia.md) | Documentación oficial de la implementación del BKT, métricas (IPF/LME/TRA), dosificación, reglas clínicas y máquina de estados diagnóstica. |

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
| Estructura de wireframes (plantilla) | frontend/Wireframes.md     |
| Lógica Clínica e Implementación BKT  | backend/MotorInferencia.md |
| Estrategia de QA y Suite de Pruebas  | entorno/Testing.md         |

---

### 🔜 Pendientes — Bloque 1 · Frontend

| Área                                                   | Documento destino      | Prioridad |
| ------------------------------------------------------ | ---------------------- | --------- |
| Wireframes Modo Niño (13 pantallas)                    | frontend/Wireframes.md | 🔴 Alta   |
| Wireframes Modo Padres (7 pantallas)                   | frontend/Wireframes.md | 🔴 Alta   |
| Sistema de diseño (colores, tipografía)                | frontend/Wireframes.md | 🔴 Alta   |
| Diseño visual del Avatar (nombre, estilo, animaciones) | frontend/Wireframes.md | 🟡 Media  |
| Especificación de Minijuegos (mecánicas de juego)      | frontend/Wireframes.md | 🟡 Media  |

---

### 🔜 Pendientes — Bloque 2 · Backend

| Área                                                | Documento destino              | Prioridad |
| --------------------------------------------------- | ------------------------------ | --------- |
| Seeding del grafo ArcadeDB (hitos + aristas)        | backend/GrafoConocimiento.md   | 🔴 Alta   |
| Intervención del tutor (ajuste R0 y salto de hitos) | backend/IntervencionTutor.md   | 🟡 Media  |
| Algoritmo de repetición espaciada (técnico)         | backend/RepeticionEspaciada.md | 🟡 Media  |
| Lógica de traducción de métricas para padres        | backend/DashboardPadres.md     | 🟡 Media  |
| Manejo de errores y logging (estándar FastAPI)      | backend/ErroresLogging.md      | 🟢 Baja   |

---

### 🔜 Pendientes — Bloque 3 · Transversal (paralelo al desarrollo)

| Área                                           | Documento destino             | Prioridad |
| ---------------------------------------------- | ----------------------------- | --------- |
| Biblioteca informativa para padres (artículos) | contenido/BibliotecaPadres.md | 🟡 Media  |
