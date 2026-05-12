# Estrategia de Testing — Backend y Frontend
> 🔜 Pendiente · Prioridad: 🟡 Media

---

## Qué es este documento

Define qué se prueba, con qué herramientas y cómo se organiza la estrategia de testing para el prototipo de Appfasia. El objetivo es detectar regresiones tempranas en el motor de inferencia (BKT, diagnóstico) y los endpoints críticos de la API.

---

## Contexto del proyecto

El motor de inferencia (BKT + RulesEngine + métricas) es el componente más sensible del sistema. Un error aquí puede afectar el progreso clínico del niño. Los endpoints de sesión y diagnóstico son los de mayor complejidad. El frontend tiene lógica de estado (máquina de estados del ejercicio, timers) que también requiere cobertura.

---

## Qué hay que definir

### 1. Herramientas

**Backend:**
```
Framework de tests:  pytest
HTTP client para tests de integración: httpx (AsyncClient)
Mocking de servicios externos: [ ] (pytest-mock, respx?)
Base de datos de tests: [ ] (¿PostgreSQL en Docker? ¿SQLite en memoria?)
Fixtures de datos: [ ] (¿factory_boy? ¿fixtures manuales?)
```

**Frontend:**
```
Framework de tests: [ ] (Vitest + React Testing Library)
Tests E2E: [ ] (Playwright? ¿Para el prototipo o solo unitarios?)
```

### 2. Qué se prueba (Backend)

**Tests unitarios — Motor de Inferencia (prioridad máxima):**

| Módulo | Qué probar |
|---|---|
| `bkt/updater.py` | Actualización correcta de P(L\|t) con distintos parámetros |
| `bkt/updater.py` | El umbral de maestría se detecta en el momento correcto |
| `rules/rules_engine.py` | Cada regla If-Then produce la acción esperada |
| `diagnostic/evaluator.py` | Regla de Piso (3 aciertos + TRA < 4s) |
| `diagnostic/evaluator.py` | Regla de Techo (3 errores consecutivos) |
| `diagnostic/result_calculator.py` | `nivel_detectado` correcto para cada escenario |
| `metrics/ipf.py` | `editex` calcula la distancia fonética correctamente |
| `metrics/lme.py` | spaCy cuenta morfemas correctamente en ejemplos conocidos |

**Tests de integración — Endpoints críticos:**

| Endpoint | Escenario a probar |
|---|---|
| `POST /auth/login` | Credenciales válidas e inválidas |
| `POST /diagnostic/start` | Se genera ejercicio correcto para la edad |
| `POST /diagnostic/response` | Secuencia completa de 9 respuestas → nivel detectado |
| `POST /session/start` | Límite diario rechaza correctamente |
| `POST /session/response` | Audio con IPF alto → SUCCESS, IPF bajo → RETRY |
| `POST /session/response` | Timeout → intento nulo registrado |
| `POST /session/response` | 3 IPF bajos → hardware_override T-S |

### 3. Qué se prueba (Frontend)

**Tests unitarios:**

| Componente / Hook | Qué probar |
|---|---|
| `useTimer.ts` | Timer de 5s dispara pista, timer de 10s dispara timeout |
| `useExerciseFlow.ts` | Transiciones de estado correctas (IDLE → PRESENTING → AWAITING → etc.) |
| `useAudioRecorder.ts` | El recorder inicia y detiene correctamente |

**Tests de integración (con React Testing Library):**

| Componente | Escenario |
|---|---|
| `Nombrador.tsx` | Render con JSON mock, botón de micrófono visible |
| `Identificador.tsx` | Tap en opción correcta → llama a callback con id correcto |
| `Constructor.tsx` | Drag & drop reordena bloques |

### 4. Datos de prueba (fixtures)

```
¿Se usan fixtures estáticas o factories dinámicas?

Datos mínimos necesarios:
  - Un tutor de prueba (email/password conocidos)
  - Un niño de prueba (sin diagnóstico y con diagnóstico completado)
  - 10 recursos en PostgreSQL (2 por nivel)
  - Estado Redis de sesión activa (para tests de session/response)

¿Cómo se limpian los datos entre tests? [ ]
  - [ ] Rollback de transacción (más rápido)
  - [ ] Truncate de tablas (más limpio)
```

### 5. Cobertura mínima objetivo

```
Motor de inferencia (bkt/, rules/, diagnostic/): [ ]% (sugerido: ≥ 80%)
Endpoints de API (integración):                  [ ]% (sugerido: ≥ 60%)
Frontend (hooks críticos):                       [ ]% (sugerido: ≥ 70%)
```

### 6. Integración con el entorno Docker

```
¿Los tests corren dentro de Docker o en el host?

Comando sugerido:
  docker compose exec backend pytest tests/ -v

¿Se añade un servicio separado de test en docker-compose? [ ]
¿Se mockea Redis y ArcadeDB en tests o se usa una instancia real? [ ]
```

---

## Preguntas abiertas

- [ ] ¿Se integra CI/CD (GitHub Actions) para el prototipo?
- [ ] ¿Los tests E2E con Playwright son necesarios para el prototipo o se posponen?
- [ ] ¿Cómo se mockea Azure STT en tests sin consumir cuota real?
- [ ] ¿Los tests del motor de inferencia usan el mismo ArcadeDB de desarrollo o uno embebido?
