# Contrato de API — Appfasia
> **Base URL:** `https://api.appfasia.com/api/v1`  
> **Autenticación:** `Authorization: Bearer <JWT>` en todos los endpoints salvo los de Auth  
> **Formato:** JSON (`Content-Type: application/json`)  
> **Versión:** 0.1

---

## Convenciones Generales

### Respuesta de error estándar
```json
{
  "error": "CHILD_NOT_FOUND",
  "message": "El perfil de niño con id 'abc-123' no existe o no pertenece a este tutor.",
  "status": 404
}
```

### Códigos de error del motor de inferencia
| Código | Significado |
|---|---|
| `SESSION_LIMIT_REACHED` | Se alcanzó el límite diario de la sesión (dosificación AAP) |
| `DIAGNOSTIC_REQUIRED` | El niño no tiene diagnóstico inicial — debe completarlo primero |
| `LOW_CONFIDENCE_AUDIO` | Azure STT no pudo procesar el audio con suficiente confianza |
| `TIMEOUT_REGISTERED` | Silencio de 10s registrado como intento nulo |
| `HARDWARE_OVERRIDE` | El motor cambió la modalidad de V-M a T-S por bloqueo fonológico |

---

## Módulo 1 · Auth

### `POST /auth/register`
Registro de un tutor (padre/cuidador).

**Request:**
```json
{
  "nombre":    "María González",
  "email":     "maria@email.com",
  "password":  "S3cur3P@ss"
}
```
**Response `201`:**
```json
{
  "id_tutor":   "uuid-tutor-001",
  "nombre":     "María González",
  "email":      "maria@email.com",
  "created_at": "2026-05-12T20:00:00Z"
}
```

---

### `POST /auth/login`
Autenticación. Devuelve el par de tokens JWT.

**Request:**
```json
{
  "email":    "maria@email.com",
  "password": "S3cur3P@ss"
}
```
**Response `200`:**
```json
{
  "access_token":  "<JWT>",
  "refresh_token": "<JWT_refresh>",
  "token_type":    "bearer",
  "expires_in":    3600
}
```
> El `access_token` expira en 1 hora. El `refresh_token` en 30 días.

---

### `POST /auth/refresh`
Renueva el `access_token` usando el `refresh_token`.

**Request:**
```json
{ "refresh_token": "<JWT_refresh>" }
```
**Response `200`:**
```json
{
  "access_token": "<nuevo_JWT>",
  "expires_in":   3600
}
```

---

### `GET /auth/me`
Devuelve el perfil del tutor autenticado.

**Response `200`:**
```json
{
  "id_tutor":   "uuid-tutor-001",
  "nombre":     "María González",
  "email":      "maria@email.com",
  "children":   ["uuid-child-001", "uuid-child-002"]
}
```

---

## Módulo 2 · Children (Perfiles de Niños)

### `POST /children`
Crea un perfil de niño asociado al tutor autenticado.

**Request:**
```json
{
  "nombre":     "Lucía",
  "fecha_nac":  "2020-03-15"
}
```
**Response `201`:**
```json
{
  "id_child":       "uuid-child-001",
  "nombre":         "Lucía",
  "fecha_nac":      "2020-03-15",
  "edad_meses":     62,
  "nivel_actual":   null,
  "diagnostico_completado": false,
  "created_at":     "2026-05-12T20:00:00Z"
}
```
> `nivel_actual: null` indica que el diagnóstico inicial aún no se ha realizado.

---

### `GET /children`
Lista todos los niños del tutor autenticado.

**Response `200`:**
```json
[
  {
    "id_child":   "uuid-child-001",
    "nombre":     "Lucía",
    "edad_meses": 62,
    "nivel_actual": 2,
    "diagnostico_completado": true,
    "ultima_sesion": "2026-05-11T18:30:00Z"
  }
]
```

---

### `GET /children/{child_id}`
Detalle completo de un perfil de niño.

**Response `200`:**
```json
{
  "id_child":     "uuid-child-001",
  "nombre":       "Lucía",
  "fecha_nac":    "2020-03-15",
  "edad_meses":   62,
  "nivel_actual": 2,
  "diagnostico_completado": true,
  "bkt_summary": {
    "hitos_dominados":   12,
    "hitos_en_practica": 3,
    "hitos_bloqueados":  1
  },
  "racha_dias": 5
}
```

---

### `PUT /children/{child_id}`
Actualiza datos del perfil (solo nombre o fecha de nacimiento).

**Request:**
```json
{ "nombre": "Luci" }
```
**Response `200`:** mismo esquema que `GET /children/{child_id}`

---

## Módulo 3 · Diagnostic (Evaluación Diagnóstica Inicial)

El diagnóstico implementa el algoritmo **Basal/Ceiling** de la Sección 14 del plan. Es una conversación de máximo 15 interacciones que determina el nivel real del niño.

### `POST /diagnostic/start`
Inicia la prueba diagnóstica. El motor calcula el punto de inicio (medio nivel por debajo de la edad cronológica).

**Request:**
```json
{ "child_id": "uuid-child-001" }
```
**Response `200`:**
```json
{
  "session_diag_id": "diag-uuid-001",
  "interaccion_num": 1,
  "max_interacciones": 15,
  "ejercicio": {
    "plantilla":    "Identificador",
    "hardware_req": "T-S",
    "nivel_prueba": 1,
    "prompt_audio": {
      "audio_url":      "https://cdn.appfasia.com/recursos/audios/vaca.mp3",
      "texto_estimulo": "Toca el animal que hace muuu"
    },
    "opciones": [
      { "id": "W_001", "imagen_url": "https://cdn.appfasia.com/recursos/imagenes/vaca.png" },
      { "id": "W_045", "imagen_url": "https://cdn.appfasia.com/recursos/imagenes/perro.png" },
      { "id": "W_089", "imagen_url": "https://cdn.appfasia.com/recursos/imagenes/gato.png" }
    ],
    "umbrales": { "tra_max_ms": 4000 }
  },
  "avatar_mensaje": "¡Hola! Vamos a jugar un juego. ¿Cuál hace muuu?"
}
```

---

### `POST /diagnostic/response`
Envía la respuesta de una interacción diagnóstica. El motor decide si continúa o termina (condición de Techo).

**Request:**
```json
{
  "session_diag_id": "diag-uuid-001",
  "tipo_respuesta":  "seleccion",
  "id_seleccionado": "W_001",
  "tra_ms":          2800,
  "audio_base64":    null
}
```
**Response `200` — Continúa la prueba:**
```json
{
  "estado":          "EN_CURSO",
  "interaccion_num": 2,
  "max_interacciones": 15,
  "ejercicio": { ... },
  "avatar_mensaje":  "¡Muy bien! Siguiente..."
}
```
**Response `200` — Prueba terminada (Ceiling o máximo de interacciones):**
```json
{
  "estado":           "COMPLETADO",
  "nivel_detectado":  2,
  "descripcion_nivel": "Estructuración Telegráfica y Expansión (2 a 4 años)",
  "avatar_mensaje":   "¡Lo hiciste genial! Ya sé cómo podemos jugar juntos.",
  "resumen": {
    "aciertos_consecutivos_inicio": 3,
    "errores_consecutivos_fin":     3,
    "total_interacciones":          9
  }
}
```

---

### `GET /diagnostic/result/{child_id}`
Consulta el resultado del último diagnóstico completado.

**Response `200`:**
```json
{
  "nivel_detectado":   2,
  "fecha_diagnostico": "2026-05-12T20:00:00Z",
  "total_interacciones": 9,
  "p_l0_inicial":      0.15
}
```

---

## Módulo 4 · Session (Sesión de Ejercicios)

Este es el **endpoint más crítico** del sistema. Cada llamada a `/session/response` ejecuta el pipeline completo: Azure STT → Métricas → BKT → RulesEngine → ContentEngine → respuesta.

### `POST /session/start`
Inicia una nueva sesión diaria. El motor verifica que no se haya superado el límite diario (dosificación AAP).

**Request:**
```json
{ "child_id": "uuid-child-001" }
```
**Response `200`:**
```json
{
  "session_id":         "sess-uuid-001",
  "child_id":           "uuid-child-001",
  "nivel_sesion":       2,
  "ejercicios_max":     4,
  "minijuegos_max":     1,
  "tiempo_max_min":     12,
  "ejercicio_actual": {
    "id_actividad":   "ACT_042",
    "plantilla":      "Nombrador",
    "hardware_req":   "V-M",
    "prompt_visual": {
      "imagen_url":   "https://cdn.appfasia.com/recursos/imagenes/mariposa.png",
      "texto_oculto": "Mariposa"
    },
    "instruccion_avatar": "¿Qué animal ves aquí?",
    "umbrales": {
      "ipf_min":       80,
      "tra_max_ms":    5000,
      "timeouts_max":  3
    }
  },
  "avatar_mensaje": "¡Hola, Lucía! ¿Lista para jugar? Mira bien esta imagen..."
}
```
**Response `403` — Límite diario alcanzado:**
```json
{
  "error":   "SESSION_LIMIT_REACHED",
  "message": "Lucía ya completó su sesión de hoy. ¡Vuelve mañana!",
  "proxima_sesion_disponible": "2026-05-13T00:00:00Z"
}
```

---

### `POST /session/response`
**El endpoint central.** Recibe la respuesta del niño y devuelve la decisión del motor más el siguiente ejercicio (o la señal de fin de sesión).

**Request:**
```json
{
  "session_id":     "sess-uuid-001",
  "id_actividad":   "ACT_042",
  "tipo_respuesta": "audio",
  "audio_base64":   "<base64_del_audio_wav>",
  "id_seleccionado": null,
  "orden_bloques":  null,
  "tra_ms":         3200,
  "es_timeout":     false
}
```

> `tipo_respuesta` puede ser: `"audio"` (V-M), `"seleccion"` (T-S), `"orden"` (T-A), `"timeout"`

**Response `200` — Continuar con siguiente ejercicio:**
```json
{
  "estado_sesion": "EN_CURSO",
  "decision_motor": {
    "accion":          "SIGUIENTE",
    "metricas": {
      "ipf":           83.3,
      "lme":           2.0,
      "tra_ms":        3200,
      "p_maestria":    0.62
    },
    "ema_score":       79.5,
    "hardware_override": null
  },
  "siguiente_ejercicio": {
    "id_actividad":   "ACT_043",
    "plantilla":      "Identificador",
    "hardware_req":   "T-S",
    "prompt_audio": {
      "audio_url":      "https://cdn.appfasia.com/recursos/audios/instruccion_04.mp3",
      "texto_estimulo": "Toca la ropa que usarías si hace frío"
    },
    "opciones": [
      { "id": "W_210", "imagen_url": "https://cdn.appfasia.com/recursos/imagenes/abrigo.png" },
      { "id": "W_211", "imagen_url": "https://cdn.appfasia.com/recursos/imagenes/shorts.png" },
      { "id": "W_212", "imagen_url": "https://cdn.appfasia.com/recursos/imagenes/camiseta.png" }
    ],
    "umbrales": { "tra_max_ms": 4000 }
  },
  "avatar_mensaje": "¡Casi! Inténtalo una vez más despacio."
}
```

**Response `200` — Cambio de modalidad (hardware override):**
```json
{
  "estado_sesion": "EN_CURSO",
  "decision_motor": {
    "accion":           "CAMBIO_MODALIDAD",
    "hardware_override": "T-S",
    "razon":            "IPF < 50% en 3 intentos consecutivos"
  },
  "siguiente_ejercicio": { ... },
  "avatar_mensaje": "¡Probemos de otra forma! Ahora toca la imagen correcta."
}
```

**Response `200` — Lanzar minijuego:**
```json
{
  "estado_sesion": "EN_CURSO",
  "decision_motor": {
    "accion": "MINIJUEGO",
    "tipo_minijuego": "Memorama_Auditivo"
  },
  "minijuego": {
    "id_minijuego": "MJ_003",
    "tipo":         "Memorama_Auditivo",
    "instruccion":  "Encuentra los pares que suenan igual",
    "pares": [
      { "id": "P1", "audio_url": "https://cdn.appfasia.com/recursos/audios/perro.mp3" },
      { "id": "P1_img", "imagen_url": "https://cdn.appfasia.com/recursos/imagenes/perro.png" }
    ]
  },
  "avatar_mensaje": "¡3 en fila! ¡Eres increíble! Ganaste un juego especial."
}
```

**Response `200` — Fin de sesión:**
```json
{
  "estado_sesion": "COMPLETADA",
  "resumen_sesion": {
    "ejercicios_completados": 4,
    "precision_promedio_ipf": 81.2,
    "hitos_dominados_hoy":    1,
    "racha_dias":             6
  },
  "avatar_mensaje": "¡Lo hiciste increíble hoy, Lucía! Descansa y mañana seguimos.",
  "proxima_sesion_disponible": "2026-05-13T00:00:00Z"
}
```

---

### `GET /session/current/{child_id}`
Verifica si hay una sesión activa (para resumir si el niño cerró la app).

**Response `200` — Sesión activa:**
```json
{
  "session_id":          "sess-uuid-001",
  "ejercicios_completados": 2,
  "ejercicios_max":      4,
  "ejercicio_actual":    { ... }
}
```
**Response `204` — No hay sesión activa.**

---

### `POST /session/{session_id}/end`
Termina la sesión explícitamente (el niño cierra la app o el tutor detiene la sesión).

**Response `200`:**
```json
{
  "session_id":   "sess-uuid-001",
  "estado":       "INTERRUMPIDA",
  "ejercicios_completados": 2,
  "datos_guardados": true
}
```

---

## Módulo 5 · Progress (Dashboard de Padres)

### `GET /progress/{child_id}`
Resumen ejecutivo del progreso, traducido a lenguaje para padres.

**Response `200`:**
```json
{
  "child_id":       "uuid-child-001",
  "nombre":         "Lucía",
  "nivel_actual":   2,
  "descripcion_nivel": "Estructuración Telegráfica y Expansión (2 a 4 años)",
  "racha_dias":     6,
  "resumen_semana": {
    "sesiones_completadas":  5,
    "minutos_totales":       52,
    "palabras_practicadas":  38,
    "hitos_dominados":       2
  },
  "metricas_traducidas": {
    "precision_habla":  "Su pronunciación mejoró un 12% esta semana.",
    "velocidad_respuesta": "Responde más rápido que la semana pasada.",
    "nivel_equivalente": "Su nivel de lenguaje equivale al de un niño de 3 años y 2 meses."
  },
  "alertas": [
    {
      "tipo":   "REZAGO",
      "mensaje": "Lucía tiene dificultad con los colores básicos. El sistema ya está trabajando en ello.",
      "nivel":   "INFO"
    }
  ]
}
```

---

### `GET /progress/{child_id}/sessions`
Historial de sesiones para el panel de padres.

**Query params:** `?limit=10&offset=0`

**Response `200`:**
```json
{
  "total": 23,
  "sessions": [
    {
      "session_id":    "sess-uuid-001",
      "fecha":         "2026-05-12T18:30:00Z",
      "duracion_min":  11,
      "ejercicios":    4,
      "ipf_promedio":  81.2,
      "etiqueta_tutor": null
    }
  ]
}
```

---

### `POST /progress/{child_id}/sessions/{session_id}/label`
El tutor etiqueta una sesión con factores externos (Sección 19 del plan).

**Request:**
```json
{
  "etiqueta": "Cansancio",
  "nota":     "Durmió mal la noche anterior"
}
```
> `etiqueta` puede ser: `"Cansancio"`, `"Distracción"`, `"Enfermedad"`, `"Otro"`

**Response `200`:**
```json
{
  "session_id":    "sess-uuid-001",
  "etiqueta":      "Cansancio",
  "r0_weight_ajustado": 0.2,
  "mensaje": "El rendimiento de esta sesión tendrá menos peso en el cálculo del progreso de Lucía."
}
```

---

### `POST /progress/{child_id}/external-advance`
El tutor reporta un avance observado fuera de la app (Sección 19 del plan).

**Request:**
```json
{
  "descripcion": "Hoy dijo su primera oración completa de 4 palabras en casa.",
  "id_hito_relacionado": "H_N2_001"
}
```
**Response `200`:**
```json
{
  "mensaje": "¡Excelente noticia! Hemos programado una prueba de verificación para la próxima sesión de Lucía.",
  "prueba_verificacion_programada": true
}
```

---

## Módulo 6 · Chatbot (Asistente para Padres)

### `POST /chatbot/message`
Envía un mensaje al chatbot de padres y recibe la respuesta del LLM.

**Request:**
```json
{
  "child_id":  "uuid-child-001",
  "mensaje":   "¿Qué es la disfasia y cómo puedo ayudar a Lucía en casa?",
  "historial": [
    { "rol": "user",      "contenido": "¿Qué significa IPF?" },
    { "rol": "assistant", "contenido": "El IPF es el Índice de Precisión Fonológica..." }
  ]
}
```
> `historial` contiene los últimos N turnos de la conversación (el frontend lo gestiona).  
> Máximo 10 turnos recomendado para no saturar el context window.

**Response `200`:**
```json
{
  "respuesta": "La disfasia es una dificultad en la adquisición del lenguaje durante la infancia...",
  "modelo_usado": "gemini-2.5-flash",
  "fuente_sugerida": "Si deseas profundizar, te recomiendo consultar con un logopeda especializado."
}
```

---

## Resumen de Endpoints

| Módulo | Método | Ruta | Auth | Descripción |
|---|---|---|---|---|
| Auth | POST | `/auth/register` | ❌ | Registro de tutor |
| Auth | POST | `/auth/login` | ❌ | Login → JWT |
| Auth | POST | `/auth/refresh` | ❌ | Renovar token |
| Auth | GET | `/auth/me` | ✅ | Perfil del tutor |
| Children | POST | `/children` | ✅ | Crear perfil de niño |
| Children | GET | `/children` | ✅ | Listar niños |
| Children | GET | `/children/{child_id}` | ✅ | Detalle de niño |
| Children | PUT | `/children/{child_id}` | ✅ | Actualizar niño |
| Diagnostic | POST | `/diagnostic/start` | ✅ | Iniciar diagnóstico |
| Diagnostic | POST | `/diagnostic/response` | ✅ | Responder diagnóstico |
| Diagnostic | GET | `/diagnostic/result/{child_id}` | ✅ | Resultado diagnóstico |
| Session | POST | `/session/start` | ✅ | Iniciar sesión diaria |
| Session | POST | `/session/response` | ✅ | **Enviar respuesta → motor** |
| Session | GET | `/session/current/{child_id}` | ✅ | Sesión activa actual |
| Session | POST | `/session/{session_id}/end` | ✅ | Terminar sesión |
| Progress | GET | `/progress/{child_id}` | ✅ | Dashboard resumen |
| Progress | GET | `/progress/{child_id}/sessions` | ✅ | Historial de sesiones |
| Progress | POST | `/progress/{child_id}/sessions/{session_id}/label` | ✅ | Etiquetar sesión |
| Progress | POST | `/progress/{child_id}/external-advance` | ✅ | Reportar avance externo |
| Chatbot | POST | `/chatbot/message` | ✅ | Mensaje al asistente de padres |
