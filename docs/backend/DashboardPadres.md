# Dashboard de Padres — Lógica de Traducción de Métricas
> 🔜 Pendiente · Prioridad: 🟡 Media

---

## Qué es este documento

Define cómo las métricas clínicas brutas (IPF, LME, TRA, datos BKT) se transforman en información comprensible para padres sin formación especializada. Corresponde a la lógica detrás del endpoint `GET /progress/{child_id}`.

---

## Contexto del proyecto

El contrato de API (ContratoAPI.md) ya define qué devuelve el endpoint:

```json
{
  "metricas_traducidas": {
    "precision_habla":        "Su pronunciación mejoró un 12% esta semana.",
    "velocidad_respuesta":    "Responde más rápido que la semana pasada.",
    "nivel_equivalente":      "Su nivel de lenguaje equivale al de un niño de 3 años y 2 meses."
  },
  "alertas": [
    {
      "tipo":    "REZAGO",
      "mensaje": "Lucía tiene dificultad con los colores básicos.",
      "nivel":   "INFO"
    }
  ]
}
```

Lo que falta es definir **cómo se calculan** esas frases y valores.

---

## Qué hay que definir

### 1. Traducción del IPF (Índice de Precisión Fonológica)

```
IPF es un número de 0-100% que mide la precisión en pronunciación.

¿Cómo se traduce a lenguaje para padres?

Opción A — Comparación semanal:
  ipf_semana_actual   = promedio de IPF de las últimas 7 sesiones
  ipf_semana_anterior = promedio de las 7 sesiones previas
  variacion_pct       = ((actual - anterior) / anterior) * 100

  Mensaje resultante:
  - Si variacion > 5%:   "Su pronunciación mejoró un {X}% esta semana."
  - Si variacion < -5%:  "La pronunciación bajó un {X}% esta semana. Es normal en semanas de crecimiento."
  - Si |variacion| ≤ 5%: "La pronunciación se mantiene estable esta semana."

¿Es correcta esta lógica? [ ]
¿Hay otros umbrales? [ ]
```

### 2. Traducción del TRA (Tiempo de Respuesta Auditiva)

```
TRA es el tiempo en ms que tarda el niño en responder tras el estímulo.
Valores más bajos = mejor procesamiento auditivo.

¿Cómo se compara semana a semana?
  tra_promedio_semana_actual   = [ ]
  tra_promedio_semana_anterior = [ ]

  Mensaje resultante:
  - Si baja > 500ms:    "Responde más rápido que la semana pasada."
  - Si sube > 500ms:    "Tarda un poco más en responder. Puede ser fatiga o dificultad nueva."
  - Si estable:         "Su tiempo de respuesta es similar al de la semana pasada."

¿Son correctos estos umbrales? [ ]
```

### 3. Equivalencia de nivel a "edad de desarrollo"

```
El nivel BKT del niño (1-5) debe traducirse a un rango de edad comprensible:

Nivel 1 → "desarrollo de lenguaje de 0 a 2 años"
Nivel 2 → "desarrollo de lenguaje de 2 a 4 años"
Nivel 3 → "desarrollo de lenguaje de 4 a 6 años"
Nivel 4 → "desarrollo de lenguaje de 6 a 8 años"
Nivel 5 → "desarrollo de lenguaje de 8 a 11 años"

¿Se calcula también un subnivel más preciso?
Por ejemplo: si P(maestría promedio) en Nivel 2 = 0.65:
  → "Su nivel corresponde a un niño de 3 años y 2 meses" (interpolación)

¿Se implementa esta interpolación? [ ]
¿Fórmula de interpolación? [ ]
```

### 4. Generación de Alertas

```
¿Qué condiciones disparan una alerta visible para el tutor?

Alerta tipo REZAGO:
  Condición: [ ] (ej. P(maestría) < 0.20 en un hito después de N sesiones)
  Mensaje:   [ ]
  Nivel:     INFO

Alerta tipo BLOQUEO:
  Condición: [ ] (ej. 3+ timeouts consecutivos en el mismo hito)
  Mensaje:   [ ]
  Nivel:     WARNING

Alerta tipo PROGRESO_NOTABLE:
  Condición: [ ] (ej. dominio de un hito en menos de la mitad de los intentos esperados)
  Mensaje:   [ ]
  Nivel:     SUCCESS

Alerta tipo RACHA_ROTA:
  Condición: [ ] (ej. no hubo sesión en 3+ días cuando había racha activa)
  Mensaje:   [ ]
  Nivel:     INFO
```

### 5. Resumen de la semana — cálculos

```
"sesiones_completadas":  COUNT de sesiones con estado COMPLETADA en los últimos 7 días
"minutos_totales":       SUM de (fecha_fin - fecha_inicio) en minutos, últimos 7 días
"palabras_practicadas":  COUNT DISTINCT de id_recurso en resultados_ejercicio, últimos 7 días
"hitos_dominados":       COUNT de hitos donde P(maestría) cruzó el umbral esta semana

¿Son correctas estas definiciones? [ ]
¿Hay otros datos relevantes? [ ]
```

### 6. Ventana de tiempo del dashboard

```
¿El dashboard siempre muestra los últimos 7 días?
¿O hay opción de ver los últimos 30 días?

Ventana por defecto: [ ]
¿Con filtro configurable? [ ]
```

---

## Preguntas abiertas

- [ ] ¿Las métricas traducidas usan el nombre propio del niño en los mensajes? (ej. "La pronunciación de Lucía...")
- [ ] ¿Hay un mínimo de sesiones necesarias para mostrar comparativas? ¿Qué se muestra si hay menos de 2 sesiones?
- [ ] ¿El chatbot tiene acceso a estas métricas traducidas como contexto?
- [ ] ¿Los logopedas que supervisan el caso pueden ver las métricas brutas? ¿Hay un rol diferente al de tutor?
