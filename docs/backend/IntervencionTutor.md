# Intervención del Tutor en el Modelo Estudiante
> 🔜 Pendiente · Prioridad: 🟡 Media  
> Referencia: Secciones 12 y 19 del Plan de Proyecto

---

## Qué es este documento

Define cómo las acciones del tutor (etiquetado de sesiones y reporte de logros externos) impactan directamente en el motor de inferencia. Son los únicos dos mecanismos por los que un humano puede influir en los cálculos del BKT y la fórmula EMA.

---

## Contexto del proyecto

### Fórmula EMA (ya definida en ArquitecturaTecnica.md)

```
Competencia actual = (R0 * 0.5) + (R-1 * 0.3) + (R-2 * 0.2)

R0  = rendimiento de la sesión actual (peso: 50%)
R-1 = rendimiento de la sesión anterior (peso: 30%)
R-2 = rendimiento de hace dos sesiones (peso: 20%)
```

El problema: si el niño tuvo un mal día por fiebre y la sesión fue horrible, R0 degrada el nivel calculado injustamente. El tutor puede corregir esto etiquetando la sesión.

### Mecanismo 1 (Sección 19 del Plan)
> *"El padre puede marcar una sesión con etiquetas como 'Cansancio', 'Distracción' o 'Enfermedad'. El motor reduce automáticamente el peso de R0 en la fórmula de competencia actual."*

### Mecanismo 2 (Sección 19 del Plan)
> *"El tutor puede informar si el niño ha mostrado avances en su entorno natural (fuera de la app), lo que permite al motor programar pruebas de 'salto de hito' para verificar si el usuario está listo para niveles superiores sin completar todos los ejercicios intermedios."*

---

## Qué hay que definir

### 1. Etiquetas de sesión disponibles

El ContratoAPI.md ya define el endpoint `POST /progress/:child_id/sessions/:session_id/label`. Las etiquetas definidas son:

| Etiqueta | Código | Descripción |
|---|---|---|
| Cansancio | `CANSANCIO` | El niño estaba somnoliento o con poca energía |
| Distracción | `DISTRACCION` | El ambiente estaba ruidoso o el niño desenfocado |
| Enfermedad | `ENFERMEDAD` | El niño estaba malo (fiebre, dolor, etc.) |
| Otro | `OTRO` | Motivo libre en campo de texto |

¿Se añaden más etiquetas? [ ]

### 2. Ajuste de R0 según la etiqueta

Este es el punto no definido más crítico. El plan dice "reduce el peso de R0" pero no especifica cuánto:

```
Opción A — Factor de penalización por etiqueta:
  CANSANCIO  → R0 * 0.30  (fue peor de lo normal, pero no ignorar)
  DISTRACCION → R0 * 0.25
  ENFERMEDAD  → R0 * 0.10  (casi ignorar esta sesión)
  OTRO        → R0 * 0.30

¿Son correctos estos factores? [ ]

Opción B — R0 se descarta completamente (peso = 0):
  Pros: Más simple
  Cons: Pierde el "mínimo dato clínico" de la sesión

¿Cuál es la opción correcta? [ ]
```

**Fórmula con ajuste (esquema a completar):**
```python
def calcular_ema_ajustada(r0, r1, r2, etiqueta_sesion=None):
    factor_r0 = {
        None:          0.50,
        "CANSANCIO":   [ ],   # definir
        "DISTRACCION": [ ],   # definir
        "ENFERMEDAD":  [ ],   # definir
        "OTRO":        [ ],   # definir
    }.get(etiqueta_sesion, 0.50)

    # Renormalizar los pesos para que sumen 1.0
    # [ ] ¿Los pesos de R-1 y R-2 absorben el peso cedido por R0, o se mantienen?
    # Ejemplo si R0 baja a 0.10:
    #   ¿R-1 = 0.60, R-2 = 0.30?  (redistribuir proporcional)
    #   ¿R-1 = 0.30, R-2 = 0.20 + un "vacío" del 40%?  (no redistribuir)

    return (r0 * factor_r0) + (r1 * 0.30) + (r2 * 0.20)
```

### 3. ¿Cuándo se aplica el ajuste?

```
¿El ajuste de R0 afecta solo el cálculo de la sesión actual,
o modifica retroactivamente el historial?

Opción A: Solo afecta el cálculo EMA del día del etiquetado
Opción B: Se recalcula el nivel del niño incluyendo la sesión etiquetada

¿Cuál? [ ]

¿El tutor puede etiquetar una sesión de hace 3 días?
  - ¿Hay un límite de tiempo para etiquetar? [ ]
```

### 4. Intervalo de tiempo para etiquetar

```
¿El tutor puede etiquetar solo la sesión del mismo día?
¿O puede etiquetar cualquier sesión del historial?

Límite sugerido: [ ] días después de la sesión
```

---

## Mecanismo 2: Reporte de Avance Externo ("Salto de Hito")

### 5. ¿Qué puede reportar el tutor?

```
Cuando el tutor activa P-07 (Modal Reporte de Avance Externo), ¿qué información envía?

Campos del reporte:
  - descripcion_texto: str   → "Hoy Lucía dijo tres oraciones seguidas jugando"
  - id_hito (opcional): str  → El tutor puede señalar un hito específico si sabe cuál
  - nivel_observado: int     → ¿O se infiere del hito seleccionado?

¿El tutor puede seleccionar un hito de una lista? [ ]
¿O es siempre texto libre y el sistema interpreta con el LLM? [ ]
```

### 6. ¿Qué hace el motor cuando recibe un reporte externo?

El plan dice "programa una prueba de salto de hito". Esto no está especificado técnicamente:

```
Opción A — Prueba de verificación automática:
  El motor programa un ejercicio de verificación del hito reportado
  en la próxima sesión (con flag is_verification = true).
  Si el niño supera la verificación → el hito se marca como dominado.
  Si falla → se ignora el reporte, el hito sigue en cola normal.

Opción B — Aumento temporal de P(L0):
  El motor aumenta temporalmente el P(L0) del hito reportado
  y deja que el BKT lo confirme naturalmente en las siguientes sesiones.

¿Cuál es el mecanismo correcto? [ ]
```

### 7. ¿Cuántas pruebas de verificación se necesitan para confirmar el salto?

```
¿Una sola sesión de verificación es suficiente? [ ]
¿O se necesitan N sesiones consecutivas con IPF >= umbral? [ ]
```

### 8. Impacto en el grafo ArcadeDB

```
Cuando se confirma un salto de hito por avance externo:
¿Los hitos intermedios (que el niño no completó) se marcan como dominados?
¿O quedan como "pendientes de práctica" aunque el niño ya esté en niveles superiores?

Esto afecta la detección de Tickets de Rezago (Sección 13).
[ ] Definir comportamiento exacto.
```

---

## Preguntas abiertas

- [ ] ¿El ajuste por etiqueta impacta también el P(L0) del BKT para el hito trabajado ese día?
- [ ] ¿El tutor recibe confirmación visual de que su etiqueta fue procesada por el motor?
- [ ] ¿Hay un límite de reportes externos por semana para evitar manipulación del sistema?
- [ ] Si el motor rechaza un "salto de hito" (el niño no pasó la verificación), ¿se notifica al tutor?
