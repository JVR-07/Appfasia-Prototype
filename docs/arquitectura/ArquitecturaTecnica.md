# Arquitectura Técnica — Appfasia
> **Documento vivo** · Versión 0.1 · Elaborado por PM

---

## Punto 1 · Stack Tecnológico y Framework Backend

### Recomendación: **FastAPI** (no Flask)

| Criterio | Flask | **FastAPI** ✅ |
|---|---|---|
| Rendimiento | Síncrono por defecto (WSGI) | **Asíncrono nativo (ASGI)** |
| Tipado | Sin soporte nativo | **Tipado estricto con Pydantic** |
| Documentación API | Manual (Flask-RESTX) | **Automática (OpenAPI/Swagger)** |
| Websockets | Plugin externo | **Nativo** |
| Validación de datos | Manual o Marshmallow | **Automática con Pydantic** |
| Curva de aprendizaje | Baja | **Baja-Media (similar a Flask)** |

**¿Por qué FastAPI y no Flask?**

El punto crítico es el **motor de inferencia**. Las operaciones de BKT, cálculo de LME/IPF/TRA y las llamadas a modelos de speech-to-text son operaciones potencialmente lentas. FastAPI con `async/await` permite manejar múltiples sesiones simultáneamente **sin bloquearse**, algo que Flask síncrono no puede hacer eficientemente sin configuración compleja. Adicionalmente, Pydantic (el corazón de FastAPI) es perfecto para validar los JSON complejos del motor de inferencia definidos en las secciones 16-17 del plan.

### Stack Completo Propuesto

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENTE                              │
│   React + TypeScript  ·  Web (PWA)  ·  Mobile (RN)     │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS / WebSocket
┌────────────────────────▼────────────────────────────────┐
│                  BACKEND (Python)                        │
│                                                         │
│  FastAPI  ──►  Motor de Inferencia (Python puro)        │
│     │               ├── BKT Engine                      │
│     │               ├── Evaluador de Métricas            │
│     │               └── Grafo de Conocimiento            │
│     │                                                   │
│     └──►  Servicios Externos                            │
│               ├── Azure Speech Service (V-M)            │
│               └── LLM (Gemini 2.5 Flash) para Avatar    │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  CAPA DE DATOS                           │
│  PostgreSQL (SQL) · Neo4j (Grafos) · Redis (Cache)      │
└─────────────────────────────────────────────────────────┘
```

---

## Punto 2 · Capa de Datos

Basado en la **Sección 17** del plan (Arquitectura Híbrida), se propone el siguiente diseño.

### 2.1 Base de Datos Relacional — PostgreSQL

**Propósito:** Almacenar los recursos atómicos (palabras, imágenes, audios) y la información transaccional (usuarios, sesiones, resultados).

**Tablas principales:**

```sql
-- Diccionario maestro de recursos (Los Átomos - Sección 17 Fase 1)
CREATE TABLE recursos (
    id_recurso      VARCHAR(10) PRIMARY KEY,   -- "W_001"
    tipo            VARCHAR(20) NOT NULL,       -- 'palabra', 'frase', 'imagen'
    texto           TEXT,
    nivel_sugerido  SMALLINT NOT NULL,          -- 1 a 5
    fonema_objetivo VARCHAR(10),               -- "rr", "bl", "pr"
    id_categoria    INT REFERENCES categorias(id),
    dificultad_art  VARCHAR(10),               -- 'alta', 'media', 'baja'
    imagen_url      TEXT,
    audio_url       TEXT,
    tags            TEXT[]
);
-- Índices críticos para el motor de inferencia
CREATE INDEX idx_recursos_nivel ON recursos(nivel_sugerido);
CREATE INDEX idx_recursos_fonema ON recursos(fonema_objetivo);
CREATE INDEX idx_recursos_tags ON recursos USING GIN(tags);

-- Usuarios y perfiles
CREATE TABLE usuarios (
    id_usuario      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre          VARCHAR(100) NOT NULL,
    fecha_nac       DATE NOT NULL,
    id_tutor        UUID REFERENCES tutores(id),
    nivel_actual    SMALLINT DEFAULT 1,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Historial de sesiones
CREATE TABLE sesiones (
    id_sesion       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_usuario      UUID REFERENCES usuarios(id_usuario),
    fecha_inicio    TIMESTAMPTZ NOT NULL,
    fecha_fin       TIMESTAMPTZ,
    nivel_sesion    SMALLINT NOT NULL,
    etiqueta_tutor  VARCHAR(20),               -- 'Cansancio', 'Distracción'
    r0_weight       FLOAT DEFAULT 0.5,
    payload_json    JSONB                      -- sesión completa para replay
);

-- Resultados por ejercicio (métricas crudas)
CREATE TABLE resultados_ejercicio (
    id_resultado    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_sesion       UUID REFERENCES sesiones(id_sesion),
    id_recurso      VARCHAR(10) REFERENCES recursos(id_recurso),
    lme             FLOAT,
    ipf             FLOAT,
    tra_ms          INT,
    intentos        SMALLINT,
    es_minijuego    BOOLEAN DEFAULT FALSE,
    timestamp_res   TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.2 Base de Datos de Grafos — ArcadeDB ✅ *(recomendado sobre Neo4j para este proyecto)*

**¿Por qué ArcadeDB y no Neo4j?**

| Criterio | Neo4j (Community) | **ArcadeDB** ✅ |
|---|---|---|
| Licencia | GPL (copyleft) | **Apache 2.0 (permisiva, gratis)** |
| Modelos soportados | Solo grafo | **Grafo + Documento + K/V** |
| Modo embebido | Solo Enterprise (pago) | **Nativo y gratuito** |
| Alta disponibilidad | Solo Enterprise (pago) | **Incluida gratis** |
| Lenguajes de consulta | Cypher | **Cypher, SQL, Gremlin, GraphQL** |
| Compatible con drivers Neo4j | Sí | **Sí (protocolo BOLT)** |

Para un **prototipo**, ArcadeDB es la elección correcta: es completamente gratuito, más simple de instalar (un solo proceso, sin servidor separado obligatorio), y al soportar Cypher nativamente permite migrar a Neo4j en el futuro sin reescribir las queries.

**Propósito:** Implementar el Mapa de Conocimiento (Sección 13), los nodos bloqueantes y las rutas de recuperación para los Tickets de Rezago.

```cypher
// Crear un Hito (Nodo) — sintaxis Cypher, funciona igual en ArcadeDB
CREATE (h:Hito {
  id: "H_N1_003",
  descripcion: "Repite la misma sílaba 2-3 veces (ma, ma, ma)",
  nivel: 1,
  es_bloqueante: false
})

// Crear dependencia pedagógica (Arista)
MATCH (h1:Hito {id: "H_N1_003"}), (h2:Hito {id: "H_N2_001"})
CREATE (h1)-[:PREREQUISITO_DE {peso: 1.0}]->(h2)

// Query del motor: ¿Qué hitos están disponibles para este usuario?
MATCH (dominado:Hito)-[:PREREQUISITO_DE]->(siguiente:Hito)
WHERE dominado.id IN $hitos_dominados
RETURN siguiente
```

**Modelo de grafo:**
```
[H_N1_001: Imitación vocal]
        │ PREREQUISITO_DE
        ▼
[H_N1_003: Balbuceo silábico] ──── es_bloqueante: true
        │ PREREQUISITO_DE
        ▼
[H_N2_001: 5 palabras distintas]
        │ PREREQUISITO_DE
        ▼
[H_N2_007: Señala 12 objetos familiares]
```

### 2.3 Caché en Memoria — Redis

**¿Por qué necesitamos Redis y no simplemente consultamos PostgreSQL en cada respuesta?**

Imagina el flujo de una sola respuesta del niño durante un ejercicio de voz:

```
Niño habla → STT → Motor calcula IPF/LME/TRA → BKT actualiza maestría
         → ¿Cuál fue su resultado hace 2 sesiones? (para EMA)
         → ¿Qué ejercicio sigue en la cola de hoy?
         → ¿Cuántos errores consecutivos lleva? (umbral fatiga)
         → ¿Está en modo minijuego?
```

Todo esto debe resolverse en **menos de 200ms** para que la experiencia se sienta fluida para un niño. Si cada una de esas preguntas implicara una query a PostgreSQL o ArcadeDB (que viven en disco), la latencia acumulada sería de 500ms–1s fácilmente — perceptible y frustrante.

**Redis resuelve esto** guardando el estado completo de la sesión activa en RAM:

```
Redis Keys:
  session:{id_usuario}:state      → JSON con parámetros BKT actuales
  session:{id_usuario}:history    → últimas 3 respuestas (cálculo EMA)
  session:{id_usuario}:queue      → cola de ejercicios de la sesión actual
  session:{id_usuario}:streak     → contador de aciertos/errores consecutivos
  maintenance:{id_usuario}        → cola de repetición espaciada (24h/3d/7d/21d)

TTL: 24 horas (sesiones activas), 30 días (mantenimiento)
```

Al **terminar la sesión**, Redis vuelca el resumen a PostgreSQL de forma permanente. Durante la sesión, el motor lee y escribe solo en RAM.

> **Costo:** Redis es open source (licencia BSD) y **completamente gratuito** en su versión base. Para el prototipo, puede correr en el mismo servidor que FastAPI sin ningún costo adicional.

### 2.4 Almacenamiento de Archivos — Azure Blob Storage ✅

Sí, Azure tiene su equivalente directo a S3 llamado **Azure Blob Storage**. Es el servicio de almacenamiento de objetos de Azure, diseñado exactamente para este caso de uso: archivos estáticos (imágenes PNG de los recursos, audios MP3 del sistema, grabaciones del usuario).

| Característica | AWS S3 | **Azure Blob Storage** ✅ |
|---|---|---|
| Tipo | Almacenamiento de objetos | Almacenamiento de objetos |
| CDN integrado | CloudFront (separado) | **Azure CDN (integrado)** |
| Acceso HTTP directo | Sí | **Sí** |
| SDK Python | `boto3` | **`azure-storage-blob`** |
| Créditos disponibles | No | **Sí (ya los tienes)** |

**Estructura de contenedores propuesta:**
```
appfasia-assets/
├── recursos/
│   ├── imagenes/        → perro.png, vaca.png, granja.png ...
│   └── audios/          → perro.mp3, instruccion_01.mp3 ...
└── grabaciones/
    └── {id_usuario}/    → respuestas de voz del niño (análisis STT)
```

> Las URLs generadas por Azure Blob Storage son las que se almacenan en los campos `imagen_url` y `audio_url` de la tabla `recursos` en PostgreSQL. El SDK `azure-storage-blob` es **gratuito** (open source, licencia MIT).

---

## Punto 3 · Especificaciones del Motor de Inferencia

### Propuesta: Motor Híbrido en Tres Capas

```
┌─────────────────────────────────────────────────────────┐
│              MOTOR DE INFERENCIA (Python)                │
│                                                         │
│  ┌──────────────────┐  ┌──────────────────────────────┐ │
│  │  Capa 1: Reglas  │  │  Capa 2: Probabilística BKT  │ │
│  │  (IA Simbólica)  │  │  (IA de Memoria Limitada)    │ │
│  │                  │  │                              │ │
│  │  - Umbrales IPF  │  │  - P(L0), P(T), P(S), P(G)  │ │
│  │  - Umbrales TRA  │  │  - Actualización Bayesiana   │ │
│  │  - Umbrales LME  │  │  - Estado latente maestría   │ │
│  │  - Dosificación  │  │                              │ │
│  └────────┬─────────┘  └──────────────┬───────────────┘ │
│           └─────────────┬─────────────┘                 │
│                         ▼                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Capa 3: Selector de Acción (Decision Engine)   │   │
│  │  - Consulta ArcadeDB para ruta óptima             │   │
│  │  - Aplica EMA (R0*0.5 + R-1*0.3 + R-2*0.2)     │   │
│  │  - Decide: avanzar / repetir / minijuego / bajar │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 3.1 Stack Técnico del Motor

| Componente | Tecnología | Justificación |
|---|---|---|
| Lenguaje base | Python 3.11+ | Ecosistema ML, tipado mejorado |
| Librería BKT | `pyBKT` (MIT License) | Implementación académica validada, vectorizada con NumPy |
| Grafo de Conocimiento | `arcadedb` BOLT driver + `networkx` | ArcadeDB para producción, NetworkX para tests |
| Cálculo de métricas | `numpy`, `pandas` | Operaciones vectorizadas para EMA y estadísticas |
| Speech-to-Text | `azure-cognitiveservices-speech` | 5h/mes gratis (F0), misma cuenta Azure que Blob Storage |
| NLP / LME | `spacy` (es_core_news_sm) | Tokenización morfológica en español |
| Comunicación async | `asyncio` + `httpx` | Llamadas no bloqueantes a STT y LLM |

### 3.2 Flujo de una Iteración del Motor (Pseudocódigo)

```python
async def process_response(user_id: str, response: UserResponse) -> EngineDecision:

    # 1. Calcular métricas crudas
    metrics = MetricsCalculator.compute(response)
    # → lme=2.5, ipf=73.0, tra_ms=3200

    # 2. Recuperar estado BKT desde Redis
    bkt_state = await redis.get(f"session:{user_id}:state")

    # 3. Actualizar probabilidad de maestría con pyBKT
    bkt_state.p_mastery = BKTEngine.update(
        p_mastery  = bkt_state.p_mastery,
        p_transit  = bkt_state.p_T,
        p_slip     = bkt_state.p_S,
        p_guess    = bkt_state.p_G,
        correct    = (metrics.ipf >= 80)
    )

    # 4. Aplicar EMA para estado de competencia estable
    history   = await redis.get(f"session:{user_id}:history")
    ema_score = (metrics.ipf * 0.5) + (history[-1] * 0.3) + (history[-2] * 0.2)

    # 5. Evaluar reglas simbólicas (Capa 1)
    decision = RulesEngine.evaluate(metrics, ema_score, bkt_state)

    # 6. Si hay cambio de nivel, consultar ArcadeDB para ruta óptima
    if decision.requires_graph_query:
        next_node            = await arcadedb.get_next_node(user_id, decision.target_level)
        decision.next_activity = ActivitySelector.pick(next_node)

    # 7. Guardar estado actualizado
    await redis.set(f"session:{user_id}:state", bkt_state)

    return decision
```

### 3.3 Parámetros BKT Iniciales (Calibración Base)

| Parámetro | Valor Inicial | Descripción |
|---|---|---|
| P(L0) | 0.10 – 0.30 | Varía según resultado del examen diagnóstico inicial |
| P(T) | 0.20 | Probabilidad de aprender en un intento exitoso |
| P(S) | 0.10 | Probabilidad de fallo aunque el niño sepa (slip) |
| P(G) | 0.25 | Probabilidad de adivinar en T-S con 4 opciones |
| Umbral maestría | 0.80 | P(L) ≥ 0.80 → hito marcado como dominado |

> **Nota:** P(G) se ajusta dinámicamente: T-S con 2 opciones = 0.50; con 4 opciones = 0.25.

### 3.4 Estructura de Módulos

```
inference_engine/
├── bkt/
│   ├── engine.py          # Lógica BKT con pyBKT
│   └── calibrator.py      # Ajuste de parámetros por diagnóstico inicial
├── rules/
│   ├── ipf_rules.py       # Umbrales IPF (maestría, práctica, bloqueo)
│   ├── tra_rules.py       # Umbrales TRA (fluidez, latencia cognitiva)
│   ├── lme_rules.py       # Umbrales LME (telegráfico, transición)
│   └── dosage_rules.py    # Límites de sesión y minijuegos
├── graph/
│   ├── navigator.py       # Consultas ArcadeDB (ruta óptima, nodos bloqueantes)
│   └── lag_detector.py    # Detección de Tickets de Rezago
├── decision/
│   ├── engine.py          # Selector de acción final
│   └── activity_picker.py # Selección de plantilla + recursos
└── memory/
    ├── ema.py             # Cálculo del promedio móvil exponencial
    └── spaced_repetition.py # Cola de repetición espaciada
```

---

## Punto 4 · Procesamiento de Métricas Clínicas

### 4.1 LME — Longitud Media del Enunciado

**Fuente:** Texto transcrito (STT → texto, o texto escrito directamente).

**Pipeline:**
```
Audio del usuario
      │
      ▼
Google STT ──► Texto: "El perro corre muy rápido"
      │
      ▼
spaCy (es_core_news_sm)
  - Tokenización morfológica
  - Identificación de morfemas (sufijos, prefijos, inflexiones)
      │
      ▼
Conteo de morfemas: 7
LME = 7 morfemas / 1 enunciado = 7.0  → Umbral: Transición Sintáctica ✅
```

**Caso borde:** Para Niveles 1-2 (0-4 años), el STT producirá output muy corto o silencio. El módulo asigna LME=0 (no es error fonológico, es información clínica válida).

### 4.2 IPF — Índice de Precisión Fonológica

**Fuente:** Audio + palabra objetivo definida por el ejercicio.

**Pipeline:**
```
Audio usuario + Palabra objetivo ("Piedra")
      │
      ▼
Azure Speech Service (F0 — 5h/mes gratis)
  - language: "es-MX" (español latinoamericano)
  - output_format: Detailed (incluye confidence score)
  - modo: reconocimiento de voz continuo o por segmento
      │
      ▼
Transcripción: "Piera" (error en sínfon "dr")
      │
      ▼
Comparador Fonológico (distancia fonética editex)
  - Objetivo → fonemas: [p][j][e][d][r][a] = 6 fonemas esperados
  - Obtenido → fonemas: [p][j][e][r][a]    = 5 fonemas correctos
      │
      ▼
IPF = (5 / 6) * 100 = 83.3%  → Umbral de Maestría ✅
```

**Manejo de ruido:** Si la confianza del STT (`confidence`) es < 0.70, el resultado se marca `LOW_CONFIDENCE` y no penaliza al usuario. Se activa el Protocolo de Silencio (Sección 13).

**Librerías:** `azure-cognitiveservices-speech` (MIT, gratuito), `editex` (MIT).

### 4.3 TRA — Tasa de Respuesta Auditiva

**Fuente:** Timestamps registrados en el cliente (frontend).

**Pipeline:**
```
Backend emite estímulo → Frontend recibe audio
  [duración del audio: ej. 1.2s]
  timestamp_audio_end = audioElement.onended → performance.now()
                │
                │  El niño procesa y responde
                ▼
  timestamp_response = performance.now() al hacer click/tap

TRA_ms = timestamp_response - timestamp_audio_end
         → enviado en el payload de respuesta al backend
```

**Implementación React:**
```typescript
const handleAudioEnd = () => setAudioEndTime(performance.now());

const handleResponse = (answer: string) => {
  const tra_ms = Math.round(performance.now() - audioEndTime);
  submitResponse({ answer, tra_ms });
};
```

> **Decisión de diseño clave:** El backend **nunca** calcula el TRA con `datetime.now()`. Siempre confía en el timestamp del cliente para evitar que la latencia de red contamine la métrica clínica.

### 4.4 Pipeline Integrado

```python
class MetricsCalculator:
    async def compute(self, response: UserResponse) -> RawMetrics:

        lme, ipf = None, None

        if response.audio_base64:
            transcript, confidence = await self.stt_client.transcribe(response.audio_base64)
            if confidence >= 0.70:
                ipf = self.phonetic_comparator.compute_ipf(
                    target   = response.target_word,
                    observed = transcript
                )
                lme = self.lme_calculator.compute(transcript)
            else:
                return RawMetrics(is_low_confidence=True, tra_ms=response.tra_ms)

        elif response.texto_escrito:
            lme = self.lme_calculator.compute(response.texto_escrito)

        return RawMetrics(
            lme               = lme,
            ipf               = ipf,
            tra_ms            = response.tra_ms,
            is_timeout        = response.tra_ms > 10_000,
            is_low_confidence = False
        )
```

---

## Resumen de Decisiones de Arquitectura

| Componente | Decisión | Gratuito | Justificación Clave |
|---|---|---|---|
| Framework | **FastAPI** | ✅ | Async nativo, Pydantic para JSON complejos, WebSockets |
| BD Principal | **PostgreSQL** | ✅ | JSONB + índices GIN para diccionario de recursos atómicos |
| BD Grafos | **ArcadeDB** | ✅ Apache 2.0 | Multi-modelo, Cypher nativo, más simple que Neo4j para prototipo |
| Caché | **Redis** | ✅ BSD | Estado BKT en RAM para respuestas < 200ms durante la sesión |
| Archivos multimedia | **Azure Blob Storage** | ✅ (créditos) | Equivalente a S3, SDK Python gratuito, CDN integrado |
| STT | **Azure Speech Service (F0)** | ✅ 5h/mes gratis | Misma cuenta Azure que Blob Storage; streaming nativo; calidad equivalente a Google |
| NLP/LME | **spaCy** | ✅ MIT | Morfología en español, rápido, sin dependencia de LLMs |
| BKT | **pyBKT** | ✅ MIT | Librería académica validada, vectorizada con NumPy |
| Distancia fonética | **editex** | ✅ MIT | Comparación fonológica ligera sin servicios externos |
| Driver ArcadeDB | **neo4j** Python driver | ✅ Apache 2.0 | Compatible por protocolo BOLT |

---

## Punto 5 · Motor de Contenido y Plantillas

### 5.1 Lógica de Inyección de Contenido

El motor de contenido es el puente entre el Decision Engine (Punto 3) y el frontend. Cuando el motor de inferencia decide «siguiente ejercicio para el niño», el ContentEngine ejecuta una consulta SQL contra el diccionario de recursos para «rellenar» la plantilla correspondiente.

**Flujo completo de inyección:**
```
Decision Engine
  │  decision = {
  │    plantilla:  "Plantilla_Nombrador",
  │    nivel:      2,
  │    fonema:     "m",
  │    categoria:  "animales",
  │    hardware:   "V-M",
  │    num_items:  3
  │  }
  ▼
ContentEngine.build_activity(decision)
  │
  ▼
PostgreSQL ─── SELECT id_recurso, texto, imagen_url, audio_url
               FROM recursos
               WHERE nivel_sugerido = 2
                 AND fonema_objetivo = 'm'
                 AND id_categoria IN (SELECT id FROM categorias WHERE nombre='animales')
                 AND id_recurso NOT IN (SELECT id_recurso FROM session_used WHERE id_sesion = $sesion)
               ORDER BY RANDOM()
               LIMIT 3;
  │
  ▼
ActivityInstance {
  id_actividad:    "ACT_042",
  plantilla_base:  "Plantilla_Nombrador",
  hardware_req:    "V-M",
  items: [
    { texto: "Mariposa", imagen_url: "https://cdn.../mariposa.png", audio_url: "..." },
    { texto: "Mono",     imagen_url: "https://cdn.../mono.png",     audio_url: "..." },
    { texto: "Murciélago",imagen_url: "https://cdn.../murcielago.png",audio_url: "..." }
  ],
  umbral_exito_ipf: 80,
  tiempo_max_tra:   5000
}
  │
  ▼
Frontend recibe el JSON y renderiza la plantilla correspondiente
```

**Reglas de inyección (del Plan, Sección 16):**

| Regla | Implementación técnica |
|---|---|
| **No Repetición** | Tabla temporal `session_used` en Redis con los `id_recurso` ya mostrados en la sesión. Se excluyen en el `WHERE` de la query. |
| **Ajuste de TRA por nivel** | `tiempo_max_tra` se calcula en el Decision Engine: `max(3000, 5000 - (nivel * 500))` ms |
| **Regla de Modalidad** | Si `ipf_consecutivo_bajo = true` en Redis, el ContentEngine fuerza `hardware_req = "T-S"` independientemente de la plantilla base. |

### 5.2 Las Tres Plantillas Base

Cada plantilla define **qué datos espera** del ContentEngine y **qué contrato de respuesta** envía al motor:

**A. Plantilla Nombrador** (`hardware: V-M`)
```json
{
  "plantilla": "Nombrador",
  "prompt_visual": { "imagen_url": "...", "texto_oculto": "Mariposa" },
  "instruccion_avatar": "¿Qué animal ves en la pantalla?",
  "respuesta_esperada": { "tipo": "audio", "palabra_objetivo": "Mariposa" },
  "umbrales": { "ipf_min": 80, "tra_max_ms": 5000, "timeouts_max": 3 }
}
```

**B. Plantilla Identificador** (`hardware: T-S`)
```json
{
  "plantilla": "Identificador",
  "prompt_audio": { "audio_url": "...", "texto_estímulo": "Toca el animal que hace muuu" },
  "opciones": [
    { "id": "W_001", "imagen_url": "vaca.png",  "es_correcta": true },
    { "id": "W_045", "imagen_url": "perro.png", "es_correcta": false },
    { "id": "W_089", "imagen_url": "gato.png",  "es_correcta": false }
  ],
  "respuesta_esperada": { "tipo": "seleccion", "id_correcto": "W_001" },
  "umbrales": { "tra_max_ms": 4000 }
}
```

**C. Plantilla Constructor** (`hardware: T-A`)
```json
{
  "plantilla": "Constructor",
  "prompt_visual": { "imagen_url": "escena_perro_corre.png" },
  "instruccion_avatar": "Ordena las palabras para describir lo que ves",
  "bloques": [
    { "id": "B1", "texto": "corre", "pos_correcta": 2 },
    { "id": "B2", "texto": "El",    "pos_correcta": 0 },
    { "id": "B3", "texto": "perro", "pos_correcta": 1 }
  ],
  "respuesta_esperada": { "tipo": "orden", "secuencia_correcta": ["B2","B3","B1"] },
  "umbrales": { "precision_min": 100, "tra_max_ms": 8000 }
}
```

### 5.3 Entrega de Multimedia (Azure CDN)

```
Azure Blob Storage
  Container: appfasia-assets (acceso público de solo lectura)
       │
       ▼
Azure CDN endpoint: https://appfasia.azureedge.net/
       │
  ┌────┴──────────────────────────────┐
  │                                   │
  ▼                                   ▼
recursos/imagenes/perro.png    recursos/audios/perro.mp3
https://appfasia.azureedge.net/recursos/imagenes/perro.png
```

Las URLs absolutas de CDN son las que se persisten en la columna `imagen_url` / `audio_url` de la tabla `recursos`. El frontend nunca necesita saber dónde está el Blob Storage — solo consume URLs del CDN.

**Estrategia de carga en el frontend:** Las imágenes y audios del ejercicio **siguiente** se precargan (`<link rel="preload">` / `new Audio()`) mientras el niño está respondiendo el ejercicio **actual**, eliminando la percepción de carga.

---

## Punto 6 · Integración del Avatar y LLM

### 6.1 Arquitectura del Avatar

El avatar ("amigo imaginario") tiene **dos funciones**: interfaz pedagógica y soporte emocional. Lo potencia un LLM con un sistema de prompts estructurado que cambia según el estado del BKT.

**LLM principal: Google Gemini 2.5 Flash** — modelo actual de Google (mayo 2026), tier gratuito con ~250 req/día y 10 RPM. Suficiente para un prototipo donde el avatar interactúa 5-10 veces por sesión.

**Respaldo: Google Gemini 2.5 Flash-Lite** — mayor cuota gratuita (~1,000 req/día, 15 RPM) con ligeramente menor capacidad de razonamiento. Se activa automáticamente si se alcanza el límite diario de Flash.

> ⚠️ **Nota:** Gemini 1.5 Flash y Gemini 2.0 Flash entran en deprecación en **junio 2026**. Usar 2.5 Flash desde el inicio evita migraciones.

**Llamada al LLM desde FastAPI:**
```python
import google.generativeai as genai  # pip install google-generativeai (gratuito)

PRIMARY_MODEL  = "gemini-2.5-flash"       # Principal: 250 req/día gratis
FALLBACK_MODEL = "gemini-2.5-flash-lite"  # Respaldo: 1,000 req/día gratis

async def get_avatar_response(context: AvatarContext, use_fallback: bool = False) -> str:
    model_name = FALLBACK_MODEL if use_fallback else PRIMARY_MODEL
    model = genai.GenerativeModel(model_name)
    response = await model.generate_content_async(
        contents=build_prompt(context)
    )
    return response.text
```

### 6.2 Sistema de Prompts del Avatar

El avatar opera en **tres modos**, activados automáticamente por el Decision Engine según el estado BKT y las métricas de la sesión:

**Modo 1 — Soporte (cuando el niño está fallando)**
```
ACTIVADO CUANDO: IPF < 50% en 2 intentos consecutivos, o Timeout registrado

SYSTEM PROMPT:
"Eres [Nombre del avatar], el mejor amigo de [Nombre del niño].
Ahora mismo tu amigo está teniendo dificultades. Tu misión es:
1. Usar un tono cálido, tranquilo y alentador. NUNCA digas 'incorrecto' o 'mal'.
2. Proporcionar una pista semántica suave. Ejemplo: 'Pista: es un animal que vive en el mar'.
3. Si el problema persiste, proponer el minijuego de forma entusiasta: '¡Oye, hagamos algo divertido antes de continuar!'
CONTEXTO DEL NIÑO: Nivel {nivel}, hito trabajado: '{hito}', intentos fallidos: {n}.
RESPONDE EN: máximo 2 oraciones cortas, lenguaje simple de nivel {nivel}."
```

**Modo 2 — Desafío (cuando el niño está dominando)**
```
ACTIVADO CUANDO: IPF >= 80% y TRA < 4s en 3 ejercicios consecutivos

SYSTEM PROMPT:
"Eres [Nombre del avatar], emocionado porque tu amigo lo está haciendo increíble.
Tu misión es:
1. Celebrar el logro con energía y entusiasmo (usa emojis si el nivel lo permite).
2. Anunciar el reto siguiente como una aventura: '¡Ahora viene algo más emocionante!'
3. NUNCA reveles que el nivel está subiendo — preséntalo como una misión nueva.
CONTEXTO: El niño acaba de dominar '{hito}'. El próximo hito es '{siguiente_hito}'.
RESPONDE EN: máximo 2 oraciones, tono emocionado."
```

**Modo 3 — Neutro/Instructor (flujo normal)**
```
ACTIVADO CUANDO: Estado estable, sin señales de fatiga ni maestría excepcional

SYSTEM PROMPT:
"Eres [Nombre del avatar], guiando a tu amigo en una actividad de lenguaje.
Tu misión es:
1. Dar la instrucción del ejercicio de forma clara y amigable.
2. Adaptar el vocabulario al nivel del niño (Nivel {nivel} = rango de edad {rango_edad}).
3. Usar frases cortas. Para Nivel 1-2: máximo 5 palabras por instrucción.
INSTRUCCIÓN BASE: '{instruccion_plantilla}'
RESPONDE adaptando esa instrucción al nivel, sin cambiar el objetivo clínico."
```

### 6.3 Flujo de Integración Avatar ↔ Motor

```
Decision Engine
  │  decision.avatar_mode = "SUPPORT"  ← determinado por RulesEngine
  │  decision.context = { nivel, hito, intentos_fallidos, ... }
  ▼
AvatarService.get_response(mode, context)
  │
  ▼
LLM API (Gemini 2.5 Flash / Flash-Lite)  ← llamada async, ~300-800ms
  │
  ▼
Respuesta de texto del avatar
  │
  ├─► Text-to-Speech del navegador (Web Speech API — GRATUITA, nativa)
  │         window.speechSynthesis.speak(utterance)  ← sin costo
  │
  └─► Animación del avatar en el frontend (sincronizada con el audio)
```

> **Decisión clave:** Para la **voz del avatar** se usa la **Web Speech API** nativa del navegador (gratuita, sin API externa). Es suficiente para el prototipo y evita un costo adicional de TTS.

### 6.4 Chatbot para Padres

El módulo de padres usa el mismo LLM pero con un System Prompt completamente distinto — sin restricciones de longitud ni vocabulario infantil.

**Base de conocimiento (RAG simple para el prototipo):**
```
Documentos base cargados como contexto:
  ├── Glosario de términos: afasia, disfasia, dislalia, BKT, LME...
  ├── Hitos de desarrollo (Secciones 6-7 del plan de proyecto)
  ├── Estrategia de Expansión (Sección 15 del plan)
  └── FAQ: "¿Por qué el sistema limitó la sesión?", "¿Qué significa IPF?"
```

**System Prompt del chatbot de padres:**
```
"Eres un asistente especializado en trastornos del lenguaje infantil (afasia y disfasia),
desarrollado para la plataforma Appfasia. Tu audiencia son padres y cuidadores SIN
formación especializada.
REGLAS:
1. Usa lenguaje claro, empático y accesible. Evita jerga clínica sin explicación.
2. Cuando mencionas un término técnico (ej. 'LME'), explícalo en una oración.
3. Si la pregunta supera tu base de conocimientos, recomienda consultar a un logopeda.
4. NUNCA hagas diagnósticos clínicos. Solo orientes y proporciones información.
5. Si el padre reporta una señal de alerta grave, prioriza recomendar evaluación profesional.
CONTEXTO DEL USUARIO: El niño '{nombre}' tiene {edad} años y lleva {semanas} semanas
en la plataforma. Su nivel actual es {nivel}/5."
```

**Implementación para prototipo (sin RAG complejo):**
El contexto del plan de proyecto se pasa directamente en el prompt como texto plano. Para producción se reemplaza por un sistema RAG con embeddings.

---

## Punto 7 · Frontend Adaptativo

### 7.1 Stack Frontend

| Componente | Tecnología | Gratuito | Justificación |
|---|---|---|---|
| Framework | **React + TypeScript** | ✅ | Tipado seguro, ecosistema amplio |
| Bundler | **Vite** | ✅ | Setup rápido, HMR eficiente |
| Estado global | **Zustand** | ✅ MIT | Más ligero que Redux para este caso |
| Animaciones | **Framer Motion** | ✅ MIT | Animaciones del avatar y transiciones |
| Audio | **Web Audio API** (nativa) | ✅ | Captura de micrófono para V-M |
| TTS Avatar | **Web Speech API** (nativa) | ✅ | Voz del avatar sin costo externo |
| Drag & Drop | **dnd-kit** | ✅ MIT | Plantilla Constructor (T-A) |
| HTTP Client | **axios** | ✅ MIT | Llamadas al backend FastAPI |

### 7.2 Arquitectura de Componentes

```
src/
├── components/
│   ├── exercises/
│   │   ├── Nombrador.tsx       # Plantilla V-M: imagen + grabación
│   │   ├── Identificador.tsx   # Plantilla T-S: audio + opciones táctiles
│   │   └── Constructor.tsx     # Plantilla T-A: drag & drop de bloques
│   ├── avatar/
│   │   ├── AvatarDisplay.tsx   # Render del personaje + animaciones
│   │   └── AvatarSpeech.tsx    # Web Speech API + sincronización boca
│   ├── session/
│   │   ├── SessionTimer.tsx    # Límite de tiempo AAP (dosificación)
│   │   └── ProgressBar.tsx     # Barra de progreso de la sesión
│   └── ui/
│       ├── MicButton.tsx       # Botón de grabación con estados visuales
│       └── DosageScreen.tsx    # Pantalla de "¡Por hoy es suficiente!"
├── store/
│   └── sessionStore.ts         # Estado global de sesión con Zustand
├── hooks/
│   ├── useAudioRecorder.ts     # Captura de micrófono (Web Audio API)
│   ├── useTimer.ts             # TRA: timestamps con performance.now()
│   └── useExerciseFlow.ts      # Máquina de estados del ejercicio
└── pages/
    ├── ChildMode.tsx           # Modo niño: sesión + avatar
    └── ParentMode.tsx          # Modo padres: dashboard + chatbot
```

### 7.3 Máquina de Estados del Ejercicio

Cada ejercicio puede estar en uno de estos estados. La interfaz reacciona a cada transición:

```
                    ┌─────────────────┐
                    │    IDLE         │  ← Esperando que el motor envíe el ejercicio
                    └────────┬────────┘
                             │ ejercicio recibido
                             ▼
                    ┌─────────────────┐
                    │   PRESENTING    │  ← Avatar da instrucción + audio se reproduce
                    └────────┬────────┘
                             │ audio termina → iniciar TRA
                             ▼
                    ┌─────────────────┐
              ┌────►│   AWAITING      │  ← Esperando respuesta del niño
              │     └──┬──────────┬───┘
              │        │          │
         pista (5s)    │ responde  │ silencio > 10s
              │        ▼          ▼
              │  ┌──────────┐  ┌───────────┐
              └──│ HINT     │  │  TIMEOUT  │  ← "Intento nulo", no es error
                 └────┬─────┘  └─────┬─────┘
                      │              │
                      └──────┬───────┘
                             │ ambos convergen
                             ▼
                    ┌─────────────────┐
                    │   EVALUATING    │  ← Backend procesa métricas
                    └────────┬────────┘
                             │
               ┌─────────────┼──────────────┐
               ▼             ▼              ▼
         ┌──────────┐  ┌──────────┐  ┌──────────────┐
         │ SUCCESS  │  │  RETRY   │  │  MINIGAME    │
         └──────────┘  └──────────┘  └──────────────┘
```

### 7.4 Cambio de Modalidad de Hardware (V-M → T-S)

Cuando el Decision Engine detecta bloqueo fonológico (IPF < 50% en 3 intentos), envía en la respuesta `hardware_override: "T-S"`. El frontend reacciona así:

```typescript
// useExerciseFlow.ts
useEffect(() => {
  if (decision.hardware_override === 'T-S') {
    // 1. Ocultar el botón de micrófono con animación
    setHardwareMode('T-S');
    // 2. El avatar explica el cambio de forma natural
    avatar.speak("Ahora vamos a intentarlo de otra forma, ¡toca la imagen correcta!");
    // 3. Renderizar la plantilla Identificador con el mismo contenido clínico
    setActivePlantilla('Identificador');
  }
}, [decision.hardware_override]);
```

**El cambio es transparente para el niño** — el avatar lo presenta como una variación divertida, no como un fallo.

### 7.5 Manejo del Timeout (Protocolo V-M)

```typescript
// useTimer.ts — implementación del protocolo de silencio (Sección 13 del plan)
const HINT_THRESHOLD_MS   = 5_000;   // 5s → avatar da pista semántica
const TIMEOUT_THRESHOLD_MS = 10_000;  // 10s → registrar como "Intento nulo"

useEffect(() => {
  const timer5s = setTimeout(() => {
    avatar.speak(decision.hint_text);   // pista semántica del LLM
  }, HINT_THRESHOLD_MS);

  const timer10s = setTimeout(() => {
    submitResponse({ tipo: 'timeout', tra_ms: 10_000, is_timeout: true });
  }, TIMEOUT_THRESHOLD_MS);

  return () => { clearTimeout(timer5s); clearTimeout(timer10s); };
}, [exerciseState]);
```

### 7.6 Pantalla de Cierre de Sesión (Dosificación)

Cuando el backend señala que se alcanzó el límite diario (`session_limit_reached: true`), el frontend muestra una pantalla de celebración — no de interrupción:

```
┌─────────────────────────────────────────┐
│  🎉  ¡Lo hiciste genial hoy, [Nombre]! │
│                                         │
│  [Avatar festejando con animación]      │
│                                         │
│  Completaste X ejercicios               │
│  Tu racha de días: ⭐⭐⭐                │
│                                         │
│  Mañana continuamos la aventura         │
│                                         │
│  [Botón: ¡Hasta mañana!]               │
└─────────────────────────────────────────┘
```

---

## Resumen de Decisiones de Arquitectura (Actualizado)

| Componente | Decisión | Gratuito | Justificación Clave |
|---|---|---|---|
| Framework backend | **FastAPI** | ✅ | Async nativo, Pydantic, WebSockets |
| BD Principal | **PostgreSQL** | ✅ | JSONB + índices GIN para recursos atómicos |
| BD Grafos | **ArcadeDB** | ✅ Apache 2.0 | Cypher nativo, más simple que Neo4j para prototipo |
| Caché | **Redis** | ✅ BSD | Estado BKT en RAM para respuestas < 200ms |
| Archivos multimedia | **Azure Blob Storage** | ✅ (créditos) | Equivalente a S3, CDN integrado |
| STT | **Azure Speech Service (F0)** | ✅ 5h/mes gratis | Misma cuenta Azure; streaming nativo; calidad equivalente a Google Cloud Speech |
| NLP/LME | **spaCy** | ✅ MIT | Morfología en español |
| BKT | **pyBKT** | ✅ MIT | Librería académica validada |
| Distancia fonética | **editex** | ✅ MIT | Comparación fonológica sin servicios externos |
| Driver ArcadeDB | **neo4j** Python driver | ✅ Apache 2.0 | Compatible por BOLT |
| LLM Avatar/Chatbot | **Gemini 2.5 Flash** (+ Flash-Lite respaldo) | ✅ (tier gratuito) | Modelo actual de Google; 250–1,000 req/día gratis según variante |
| Framework frontend | **React + TypeScript + Vite** | ✅ | Ecosistema maduro, tipado seguro |
| Estado global | **Zustand** | ✅ MIT | Ligero, sin boilerplate |
| Drag & Drop | **dnd-kit** | ✅ MIT | Plantilla Constructor (T-A) |
| Animaciones | **Framer Motion** | ✅ MIT | Avatar + transiciones de estado |
| TTS Avatar | **Web Speech API** (nativa) | ✅ | Sin costo, integrada en el navegador |

---

*Documento completo para Puntos 1–7. Próximas definiciones pendientes según DocumentacionTecnica.md.*
