# Algoritmo Diagnóstico Inicial — Especificación Técnica (Basal/Ceiling)
> Basado en la Sección 14 del Plan de Proyecto · Versión 0.1

---

## 1. Objetivo del Algoritmo

Determinar el **nivel base real** del niño en un máximo de 15 interacciones, usando el concepto clínico de Piso y Techo, para:
1. Establecer el nivel de inicio de las sesiones regulares.
2. Calcular el valor inicial de `P(L0)` del modelo BKT para cada hito.
3. Garantizar una experiencia inicial de confianza (no frustrante).

---

## 2. Cálculo del Nivel de Inicio

### Paso 1 — Edad cronológica en meses

```python
from datetime import date

def calcular_edad_meses(fecha_nac: date) -> int:
    hoy = date.today()
    return (hoy.year - fecha_nac.year) * 12 + (hoy.month - fecha_nac.month)
```

### Paso 2 — Nivel esperado por edad

```python
def nivel_esperado(edad_meses: int) -> int:
    if edad_meses < 24:   return 1   # 0–2 años
    if edad_meses < 48:   return 2   # 2–4 años
    if edad_meses < 72:   return 3   # 4–6 años
    if edad_meses < 96:   return 4   # 6–8 años
    return 5                         # 8–11 años
```

### Paso 3 — Nivel de inicio (medio nivel por debajo)

El plan indica empezar **medio nivel por debajo** para generar confianza inicial. La implementación:

```python
def nivel_inicio(nivel_esperado: int) -> tuple[int, str]:
    """
    Retorna (nivel, dificultad_inicial).
    Siempre se inicia en la mitad ALTA del nivel inferior.
    """
    if nivel_esperado == 1:
        return (1, "baja")    # No hay nivel inferior, empezar fácil
    else:
        return (nivel_esperado - 1, "alta")  # Mitad alta del nivel anterior
```

**Ejemplos:**
| Edad | Meses | Nivel esperado | Nivel inicio | Dificultad inicio |
|---|---|---|---|---|
| 1 año | 12 | 1 | 1 | baja |
| 3 años | 36 | 2 | 1 | alta |
| 5 años | 60 | 3 | 2 | alta |
| 7 años | 84 | 4 | 3 | alta |
| 9 años | 108 | 5 | 4 | alta |

---

## 3. Máquina de Estados del Diagnóstico

```
                    ┌───────────────────┐
                    │   INITIALIZING    │  ← Se crea la sesión, se calcula el inicio
                    └────────┬──────────┘
                             │ primer ejercicio seleccionado
                             ▼
                    ┌───────────────────┐
                    │  AWAITING_BASAL   │  ← Primeras 3 respuestas
                    └────────┬──────────┘  (verificando si hay Piso)
                             │
              ┌──────────────┼──────────────────┐
              │                                  │
    3 aciertos + TRA<4s                    No se establece Piso
    (Piso establecido)                    (continuar explorando)
              │                                  │
              ▼                                  ▼
    ┌──────────────────┐             ┌───────────────────────┐
    │ Salto de nivel   │             │      EXPLORING        │
    │ nivel_actual += 1│────────────►│ (flujo normal arriba) │
    └──────────────────┘             └────────┬──────────────┘
                                              │
                          ┌───────────────────┤
                          │                   │
               3 errores/timeouts      interacciones ≥ 15
               consecutivos            (límite alcanzado)
                          │                   │
                          ▼                   ▼
                 ┌──────────────────────────────────┐
                 │       CEILING_DETECTED /          │
                 │     LIMIT_REACHED                 │
                 └──────────────┬───────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │    COMPLETED    │  ← Nivel detectado calculado
                       └─────────────────┘     P(L0) asignado
```

---

## 4. Estado de Sesión Diagnóstica en Redis

Todo el estado se guarda en Redis con TTL de 2 horas (si se abandona a mitad, se puede retomar).

```json
{
  "session_diag_id":       "diag-uuid-001",
  "child_id":              "uuid-child-001",
  "estado":                "EXPLORING",
  "interaccion_num":       5,
  "nivel_prueba_actual":   2,
  "dificultad_actual":     "media",
  "basal_establecido":     true,
  "nivel_basal":           1,
  "techo_detectado":       false,
  "nivel_techo":           null,
  "consecutivos_correctos": 1,
  "consecutivos_errores":   0,
  "items_usados":          ["W_001", "W_045", "W_089", "W_110", "W_120"],
  "historial": [
    {
      "interaccion": 1,
      "nivel":       1,
      "dificultad":  "alta",
      "id_recurso":  "W_001",
      "correcto":    true,
      "tra_ms":      2800,
      "ipf":         95.0,
      "es_timeout":  false
    },
    {
      "interaccion": 2,
      "nivel":       1,
      "dificultad":  "alta",
      "id_recurso":  "W_045",
      "correcto":    true,
      "tra_ms":      3100,
      "ipf":         88.0,
      "es_timeout":  false
    },
    {
      "interaccion": 3,
      "nivel":       1,
      "dificultad":  "alta",
      "id_recurso":  "W_089",
      "correcto":    true,
      "tra_ms":      2500,
      "ipf":         92.0,
      "es_timeout":  false
    }
  ]
}
```

---

## 5. Reglas del Algoritmo

### Regla del Piso (Basal)

```python
def verificar_basal(estado: DiagnosticState) -> bool:
    """
    Piso establecido si: 3 aciertos consecutivos al inicio
    con TRA < 4000ms cada uno.
    Solo se verifica durante el estado AWAITING_BASAL.
    """
    if estado.basal_establecido:
        return True
    if estado.interaccion_num < 3:
        return False

    ultimas_3 = estado.historial[-3:]
    return all(
        r["correcto"] and r["tra_ms"] < 4000
        for r in ultimas_3
    )
```

**Efecto:** Cuando se establece el Piso en nivel N, el sistema asume que el niño domina **todo el contenido de niveles anteriores a N** sin necesidad de evaluarlo. El `nivel_prueba_actual` salta a `nivel_basal + 1`.

---

### Regla del Techo (Ceiling — Condición de Salida)

```python
def verificar_techo(estado: DiagnosticState) -> bool:
    """
    Techo detectado si: 3 errores o timeouts consecutivos.
    Condición de salida inmediata, sin importar interacciones restantes.
    """
    if len(estado.historial) < 3:
        return False

    ultimas_3 = estado.historial[-3:]
    return all(
        not r["correcto"] or r["es_timeout"]
        for r in ultimas_3
    )
```

**Efecto:** El nivel detectado = `nivel_prueba_actual - 1` (el último nivel donde el niño respondía correctamente).

---

### Regla de Progresión entre Piso y Techo

Una vez establecido el Piso, el algoritmo sube de nivel según este criterio (más gradual que el Techo):

```python
def decidir_nivel_siguiente(estado: DiagnosticState) -> tuple[int, str]:
    """
    Retorna (nuevo_nivel, nueva_dificultad).
    """
    if estado.consecutivos_correctos >= 2:
        # 2 aciertos consecutivos en este nivel → subir de nivel
        nuevo_nivel = min(5, estado.nivel_prueba_actual + 1)
        return (nuevo_nivel, "baja")   # empezar fácil en el nuevo nivel

    if estado.consecutivos_errores == 1:
        # 1 error → bajar dificultad dentro del mismo nivel
        nueva_dificultad = {"alta": "media", "media": "baja"}.get(
            estado.dificultad_actual, "baja"
        )
        return (estado.nivel_prueba_actual, nueva_dificultad)

    # Estado neutro → mantener
    return (estado.nivel_prueba_actual, estado.dificultad_actual)
```

---

## 6. Selección de Ejercicios Durante el Diagnóstico

El diagnóstico usa **exclusivamente** la plantilla **Identificador (T-S)** — 3 opciones visuales. Razones:
- No requiere micrófono (reduce variables técnicas en la primera interacción)
- `P(G) = 1/3 = 0.33` — el BKT puede corregir por azar con este valor conocido
- Funciona en todos los niveles y edades

```python
async def seleccionar_ejercicio_diagnostico(
    estado: DiagnosticState,
    nivel: int,
    dificultad: str
) -> ActivityInstance:

    # Query al diccionario de recursos, excluyendo los ya usados
    recursos = await postgres.fetch("""
        SELECT id_recurso, texto, imagen_url, audio_url
        FROM recursos
        WHERE nivel_sugerido = $1
          AND dificultad_art = $2
          AND id_recurso != ALL($3::varchar[])
        ORDER BY RANDOM()
        LIMIT 1
    """, nivel, dificultad, estado.items_usados)

    recurso_correcto = recursos[0]

    # Seleccionar 2 distractores del mismo nivel (categoría diferente si es posible)
    distractores = await postgres.fetch("""
        SELECT id_recurso, imagen_url
        FROM recursos
        WHERE nivel_sugerido = $1
          AND id_recurso != $2
          AND id_recurso != ALL($3::varchar[])
        ORDER BY RANDOM()
        LIMIT 2
    """, nivel, recurso_correcto["id_recurso"], estado.items_usados)

    return ActivityInstance(
        plantilla="Identificador",
        hardware_req="T-S",
        prompt_audio=recurso_correcto["audio_url"],
        opciones=shuffle([recurso_correcto] + distractores),
        id_correcto=recurso_correcto["id_recurso"]
    )
```

---

## 7. Evaluación de Respuesta Diagnóstica

```python
async def evaluar_respuesta_diagnostica(
    estado: DiagnosticState,
    respuesta: DiagnosticResponse
) -> DiagnosticStepResult:

    # 1. Determinar si la respuesta es correcta
    es_correcto = (
        respuesta.id_seleccionado == estado.ejercicio_actual.id_correcto
        and not respuesta.es_timeout
    )

    # 2. Actualizar contadores consecutivos
    if es_correcto:
        estado.consecutivos_correctos += 1
        estado.consecutivos_errores = 0
    else:
        estado.consecutivos_errores += 1
        estado.consecutivos_correctos = 0

    # 3. Registrar en historial
    estado.historial.append({
        "interaccion": estado.interaccion_num,
        "nivel":       estado.nivel_prueba_actual,
        "dificultad":  estado.dificultad_actual,
        "id_recurso":  estado.ejercicio_actual.id_correcto,
        "correcto":    es_correcto,
        "tra_ms":      respuesta.tra_ms,
        "es_timeout":  respuesta.es_timeout
    })
    estado.items_usados.append(estado.ejercicio_actual.id_correcto)
    estado.interaccion_num += 1

    # 4. Verificar condiciones de salida
    if verificar_techo(estado):
        return await completar_diagnostico(estado, razon="CEILING")

    if estado.interaccion_num > 15:
        return await completar_diagnostico(estado, razon="LIMIT_REACHED")

    # 5. Verificar Piso (solo en primeras interacciones)
    if not estado.basal_establecido and verificar_basal(estado):
        estado.basal_establecido = True
        estado.nivel_basal = estado.nivel_prueba_actual
        estado.nivel_prueba_actual = min(5, estado.nivel_basal + 1)
        estado.dificultad_actual = "baja"
        estado.estado = "EXPLORING"
    else:
        # 6. Progresión normal entre Piso y Techo
        nuevo_nivel, nueva_dificultad = decidir_nivel_siguiente(estado)
        estado.nivel_prueba_actual = nuevo_nivel
        estado.dificultad_actual   = nueva_dificultad

    # 7. Guardar estado en Redis y seleccionar siguiente ejercicio
    await redis.set(f"diag:{estado.session_diag_id}", estado)
    siguiente = await seleccionar_ejercicio_diagnostico(
        estado, estado.nivel_prueba_actual, estado.dificultad_actual
    )

    return DiagnosticStepResult(estado="EN_CURSO", siguiente=siguiente)
```

---

## 8. Cálculo del Resultado Final

### Determinar el nivel detectado

```python
def calcular_nivel_detectado(estado: DiagnosticState, razon: str) -> int:
    if razon == "CEILING":
        # El techo se detectó en nivel_prueba_actual
        # El nivel real es el anterior donde respondía bien
        return max(1, estado.nivel_prueba_actual - 1)

    if razon == "LIMIT_REACHED":
        # Usar el nivel más alto donde tuvo al menos 1 acierto
        niveles_con_acierto = [
            r["nivel"] for r in estado.historial if r["correcto"]
        ]
        return max(niveles_con_acierto) if niveles_con_acierto else 1

    return estado.nivel_prueba_actual
```

### Asignar P(L0) inicial del BKT

El nivel detectado se traduce en una probabilidad de conocimiento inicial para arrancar el BKT:

| Nivel detectado | P(L0) asignado | Interpretación |
|---|---|---|
| 1 | 0.05 | Inicio absoluto — muy poca experiencia |
| 2 | 0.15 | Vocabulario básico presente |
| 3 | 0.25 | Estructuras simples consolidadas |
| 4 | 0.40 | Competencia metalingüística emergente |
| 5 | 0.55 | Nivel avanzado — consolidación en curso |

```python
P_L0_POR_NIVEL = {1: 0.05, 2: 0.15, 3: 0.25, 4: 0.40, 5: 0.55}

async def completar_diagnostico(
    estado: DiagnosticState,
    razon: str
) -> DiagnosticStepResult:

    nivel_detectado = calcular_nivel_detectado(estado, razon)
    p_l0 = P_L0_POR_NIVEL[nivel_detectado]

    # Persistir resultado en PostgreSQL
    await postgres.execute("""
        INSERT INTO diagnosticos
          (child_id, nivel_detectado, p_l0_inicial, total_interacciones,
           razon_finalizacion, historial_json, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, NOW())
    """, estado.child_id, nivel_detectado, p_l0,
         estado.interaccion_num - 1, razon,
         json.dumps(estado.historial))

    # Actualizar nivel en el perfil del niño
    await postgres.execute("""
        UPDATE usuarios SET nivel_actual = $1 WHERE id_usuario = $2
    """, nivel_detectado, estado.child_id)

    # Limpiar estado Redis
    await redis.delete(f"diag:{estado.session_diag_id}")

    return DiagnosticStepResult(
        estado="COMPLETADO",
        nivel_detectado=nivel_detectado,
        p_l0=p_l0,
        total_interacciones=estado.interaccion_num - 1
    )
```

---

## 9. Casos Borde

### Caso 1 — Niño superdotado (Piso en Nivel 4 o 5)
Si el basal se establece en Nivel 4 y se salta a Nivel 5, pero también domina el Nivel 5 → el algoritmo alcanza el límite de 15 interacciones antes de encontrar Techo.

**Manejo:** `razon = "LIMIT_REACHED"`. `nivel_detectado = 5`. Se inicia en el nivel más difícil disponible. En sesiones regulares, el motor detectará rápidamente la maestría y activará ejercicios de consolidación.

---

### Caso 2 — Perfil inconsistente (falla en niveles bajos, acierta en altos)
Ejemplo: acierta en Nivel 3 pero falla en Nivel 1 items difíciles.

**Manejo:** El algoritmo trabaja con la tendencia general (el `nivel_detectado` es estadístico). El motor de inferencia de sesiones regulares detectará el rezago aislado y creará un "Ticket de Rezago" (Sección 13 del plan) — micro-ejercicios de Nivel 1 camuflados en sesiones de Nivel 3.

---

### Caso 3 — Timeout en el primer ejercicio
El niño no responde en los primeros 10s.

**Manejo:** Se registra como error (`correcto: false`, `es_timeout: true`). El avatar ofrece ayuda: "No te preocupes, inténtalo de otra forma". El primer timeout **no** penaliza el contador de consecutivos — es un período de adaptación. A partir del segundo timeout, sí cuenta.

```python
# Excepción solo para la primera interacción
if estado.interaccion_num == 1 and respuesta.es_timeout:
    estado.consecutivos_errores = 0  # No penalizar
    estado.dificultad_actual = "baja"  # Bajar la dificultad
```

---

## 10. Estructura de Módulo en el Backend

```
inference_engine/
└── diagnostic/
    ├── __init__.py
    ├── state_machine.py     # DiagnosticState + transiciones
    ├── level_calculator.py  # calcular_edad_meses, nivel_esperado, nivel_inicio
    ├── exercise_selector.py # seleccionar_ejercicio_diagnostico
    ├── evaluator.py         # evaluar_respuesta_diagnostica
    ├── result_calculator.py # calcular_nivel_detectado, completar_diagnostico
    └── edge_cases.py        # Manejo de timeouts, perfiles inconsistentes
```
