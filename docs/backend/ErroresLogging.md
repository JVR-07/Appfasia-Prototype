# Manejo de Errores y Logging — Estándar FastAPI
> 🔜 Pendiente · Prioridad: 🟢 Baja

---

## Qué es este documento

Define el estándar de manejo de errores y logging para el backend de Appfasia: respuestas de error consistentes en toda la API, logs estructurados para depuración y estrategias de fallback para servicios externos.

---

## Contexto del proyecto

El backend integra 5 servicios externos (PostgreSQL, ArcadeDB, Redis, Azure STT, Gemini LLM). Cada uno puede fallar. Sin un estándar definido, cada endpoint manejará errores de forma distinta, dificultando el debugging.

---

## Qué hay que definir

### 1. Formato estándar de respuesta de error

El ContratoAPI.md ya define el esquema base. ¿Se añaden campos adicionales?

```json
{
  "error":      "CHILD_NOT_FOUND",
  "message":    "El perfil de niño no existe.",
  "status":     404,
  "request_id": "[ ]",
  "timestamp":  "[ ]"
}
```

### 2. Catálogo de códigos de error del dominio

| Código | HTTP | Módulo | Cuándo ocurre |
|---|---|---|---|
| `CHILD_NOT_FOUND` | 404 | Children | El `child_id` no existe o no pertenece al tutor |
| `SESSION_LIMIT_REACHED` | 403 | Session | Límite diario alcanzado |
| `DIAGNOSTIC_REQUIRED` | 403 | Session | Sin diagnóstico completado |
| `LOW_CONFIDENCE_AUDIO` | 422 | Session | Azure STT no procesó el audio |
| `INVALID_CREDENTIALS` | 401 | Auth | Email o contraseña incorrectos |
| `TOKEN_EXPIRED` | 401 | Auth | JWT expirado |
| `[ ]` | [ ] | [ ] | [ ] |

### 3. Estrategia de logging

```
Librería sugerida: structlog (JSON estructurado) o logging estándar
¿Cuál usar? [ ]

Nivel de log por entorno:
  development: DEBUG
  production:  INFO

Campos mínimos por log:
  timestamp, level, module, request_id, child_id (si aplica), message, error
```

### 4. Fallback de servicios externos

**Azure STT:**
```
Fallos: [ ] reintentos, backoff de [ ] segundos
Fallback: [ ] (¿marcar LOW_CONFIDENCE? ¿pedir repetición?)
```

**Gemini LLM:**
```
Fallos: [ ] reintentos
Fallback: [ ] (¿respuesta predefinida? ¿cambiar a Flash-Lite?)
¿El ejercicio continúa sin respuesta del avatar? [ ]
```

**ArcadeDB:**
```
Fallback: [ ] (¿NetworkX en memoria como respaldo?)
```

**Redis:**
```
¿El sistema opera sin caché? [ ]
Fallback: [ ]
```

### 5. Monitoreo

```
¿Se integra alguna herramienta?
  - [ ] Logs a archivo local (suficiente para prototipo)
  - [ ] Azure Monitor (disponible con créditos)
  - [ ] Sentry (tier gratuito)
  - [ ] Ninguno por ahora
```

---

## Preguntas abiertas

- [ ] ¿Los errores de validación Pydantic (422) usan el mismo formato?
- [ ] ¿Se añade `request_id` único por petición para rastrear logs?
- [ ] ¿En producción se oculta el detalle del error interno al cliente?
