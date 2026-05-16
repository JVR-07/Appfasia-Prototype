# Estrategia de Testing — Backend y Frontend

---

## Qué es este documento

Define qué se prueba, con qué herramientas y cómo se organiza la estrategia de testing para el prototipo de Appfasia. El objetivo es detectar regresiones tempranas en el motor de inferencia (BKT, diagnóstico) y los endpoints críticos de la API.

---

## Contexto del proyecto

El motor de inferencia (BKT + RulesEngine + métricas) es el componente más sensible del sistema. Un error aquí puede afectar el progreso clínico del niño. Por ello, el **Sprint 1** se enfocó exclusivamente en probar matemáticamente y clínicamente el motor.

---

## 1. Herramientas Implementadas

**Backend:**

```bash
Framework de tests:  pytest
Tests Asíncronos:    pytest-asyncio
Mocking de Redis:    fakeredis (Redis en memoria, instantáneo)
Mocking general:     unittest.mock (para Azure STT y Gemini)
Base de datos:       Para la lógica pura, no se requiere BD real; se inyectan Dataclasses/Mocks.
```

**Frontend (Pendiente):**

```bash
Framework de tests: Vitest + React Testing Library
Tests E2E: Pospuestos para post-prototipo (Playwright no se usará inicialmente).
```

---

## 2. Cobertura del Motor de Inferencia (Sprint 1)

El motor cuenta con **124 tests automatizados**, asegurando cobertura completa en lógica pura:

| Módulo                    | Pruebas Implementadas                                                                             | Archivo               |
| ------------------------- | ------------------------------------------------------------------------------------------------- | --------------------- |
| `bkt/engine.py`           | Absorción de P(L), límites matemáticos [0,1], impacto de adivinanza (P(G)) y calibración `P(L0)`. | `test_bkt_engine.py`  |
| `rules/*.py`              | Todas las ramas condicionales para LME, TRA, e IPF. Reglas de _Override_ de hardware.             | `test_rules.py`       |
| `diagnostic/evaluator.py` | Test _end-to-end_ del State Machine. Detección Basal/Ceiling y gracia de timeout.                 | `test_diagnostic.py`  |
| `metrics/ipf.py`          | Cálculo fonológico con `py-stringmatching`, manejo de acentos y strings vacíos.                   | `test_metrics_ipf.py` |
| `metrics/lme.py`          | Conteo morfológico con `spaCy`, ignorando puntuación.                                             | `test_metrics_lme.py` |
| `rules/dosage.py`         | Límites AAP de tiempo/ejercicios por nivel. Prioridad de minijuegos.                              | `test_dosage.py`      |
| `memory/ema.py`           | Promedios Móviles Exponenciales (EMA) y triggers de degradación de nivel.                         | `test_ema.py`         |

### 3. Cobertura Lograda

Al finalizar la Sprint 3, la suite de pruebas ha crecido a **287 tests** que pasan exitosamente:

```bash
Motor de inferencia (bkt/, rules/, diagnostic/): 100% cubierto.
Métricas Clínicas (IPF, LME, SEM con LLM mock):  100% cubierto.
Endpoints de API (integración con TestClient):   100% cubierto.
Frontend (hooks críticos):                       Pendiente (Sprint 4)
```

**Estrategia de Integración (Sprint 3):**
Para probar la API (`/api/v1/*`) de forma rápida sin levantar Docker, se implementó una estrategia avanzada de Mocking en `tests/api/conftest.py`:

- `mock_db`: Simula `asyncpg.Pool` devolviendo diccionarios predefinidos para los repositorios.
- `fake_redis`: Instancia real en memoria pero efímera para probar manejo de estados.
- `dependency_overrides`: Sobrescribe las inyecciones de dependencias de FastAPI durante la inicialización del `TestClient`.

---

## 4. Ejecución del Entorno (Local)

Dado que se usan dependencias locales (como `fakeredis`), la suite se ejecuta instantáneamente sin levantar Docker:

```bash
source backend/venv/bin/activate
pytest -v backend/tests/
```

---

## Respuestas a Preguntas Abiertas Originales

- **¿Se integra CI/CD (GitHub Actions)?** Sí, se puede ejecutar `pytest` en CI al no depender de contenedores pesados.
- **¿Tests E2E con Playwright?** Descartados para la fase de prototipo por costo de mantenimiento.
- **¿Cómo se mockea Azure STT?** Se utiliza `unittest.mock` para simular retornos de transcripción y niveles de confianza (`confidence`), evitando consumir la cuota gratuita (F0) de Azure.
- **¿Cómo se mockea ArcadeDB?** Para las reglas puras, se inyectan las opciones directamente en las interfaces de selección (`Protocols`). La integración real con ArcadeDB se probará en el Sprint 2.
