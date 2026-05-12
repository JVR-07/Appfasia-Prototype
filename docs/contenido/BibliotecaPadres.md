# Biblioteca Informativa para Padres — Estrategia de Contenido
> 🔜 Pendiente · Prioridad: 🟡 Media  
> Referencia: Sección 15 del Plan de Proyecto

---

## Qué es este documento

Define la estrategia de contenido de la Biblioteca Informativa del Modo Padres: qué artículos existen, su estructura, quién los redacta y cómo se integran como base de conocimiento del chatbot de padres.

---

## Contexto del proyecto

### Rol en la app

La Biblioteca es la sección informativa del Modo Padres (pantalla P-02, no wireframed aún). Sirve para dos propósitos:

1. **Educativo:** El tutor puede leer artículos sobre afasia, disfasia y estrategias para casa.
2. **RAG del chatbot:** Los artículos se pasan como contexto al LLM (Gemini 2.5 Flash) para que el chatbot pueda responder preguntas con información validada del proyecto, sin "alucinar" datos clínicos.

### Cómo se usa en el chatbot (ArquitecturaTecnica.md Punto 6.4)

```
El System Prompt del chatbot incluye los artículos como texto plano:
  "Eres un asistente... [System Prompt]
  
  DOCUMENTACIÓN DE REFERENCIA:
  --- ARTÍCULO 1: ¿Mi hijo está tardando en hablar? ---
  [contenido del artículo]
  --- ARTÍCULO 2: Estrategia de Expansión ---
  [contenido del artículo]
  ..."
```

Para el prototipo, todos los artículos se incluyen en el prompt. En producción se reemplaza por un sistema RAG con embeddings.

### Artículos base definidos en el Plan (Sección 15)

El plan ya menciona dos artículos concretos:

1. **"¿Mi hijo está tardando en hablar? Signos de alerta a los 2 años"**
   - Clasificación: Detección Temprana / Alertas
   - Fuente: CDC — "Aprenda los signos. Reaccione pronto", 2022

2. **"Estrategia de Expansión: Cómo corregir sin frustrar"**
   - Clasificación: Recomendaciones Prácticas / Hogar
   - Fuente: Owens, R.E. (2020), *Language Development: An Introduction*

---

## Qué hay que definir

### 1. Catálogo completo de artículos

El plan define 2 artículos de ejemplo. ¿Cuántos artículos totales necesita el prototipo?

**Artículos sugeridos por categoría:**

#### Categoría: Detección Temprana

| # | Título | Edad objetivo | Estado |
|---|---|---|---|
| A-01 | ¿Mi hijo está tardando en hablar? Signos de alerta a los 2 años | 0-2 años | 📝 Por redactar |
| A-02 | Señales de alerta en el habla de niños de 3 a 5 años | 3-5 años | 📝 Por redactar |
| A-03 | Cuándo consultar a un logopeda | Todas | 📝 Por redactar |

#### Categoría: Recomendaciones Prácticas para el Hogar

| # | Título | Técnica base | Estado |
|---|---|---|---|
| A-04 | Estrategia de Expansión: Cómo corregir sin frustrar | Owens 2020 | 📝 Por redactar |
| A-05 | Cómo hablarle a tu hijo para estimular el lenguaje | [ ] | 📝 Por redactar |
| A-06 | Juegos en casa para trabajar el vocabulario | [ ] | 📝 Por redactar |
| A-07 | La importancia de la lectura en voz alta | [ ] | 📝 Por redactar |

#### Categoría: Información sobre Diagnósticos

| # | Título | Estado |
|---|---|---|
| A-08 | ¿Qué es la disfasia? Guía para padres | 📝 Por redactar |
| A-09 | ¿Qué es la afasia? Cuando el lenguaje se pierde | 📝 Por redactar |
| A-10 | Diferencia entre dislalia y retraso del lenguaje | 📝 Por redactar |

#### Categoría: Entendiendo la plataforma

| # | Título | Estado |
|---|---|---|
| A-11 | ¿Cómo funciona la evaluación diagnóstica de Appfasia? | 📝 Por redactar |
| A-12 | ¿Qué significan las métricas? Guía para interpretar el progreso | 📝 Por redactar |
| A-13 | ¿Por qué el sistema limita las sesiones diarias? | 📝 Por redactar |

¿Se añaden o eliminan artículos? [ ]
¿Cuántos son necesarios para el prototipo funcional? [ ] (sugerido: mínimo 5)

---

### 2. Estructura de cada artículo

Cada artículo debe tener una estructura consistente para poder ser procesado por el chatbot y mostrado en la UI:

```json
{
  "id_articulo":     "A-01",
  "titulo":          "¿Mi hijo está tardando en hablar?",
  "subtitulo":       "Signos de alerta a los 2 años",
  "categoria":       "Detección Temprana",
  "tags":            ["2 años", "signos de alerta", "detección temprana"],
  "nivel_lectura":   "básico",
  "tiempo_lectura":  "3 min",
  "resumen":         "Una descripción de 2 oraciones para la lista de artículos",
  "contenido_md":    "## Título\n\nContenido en Markdown...",
  "fuentes":         ["CDC, 2022 — Aprenda los signos. Reaccione pronto"],
  "disclaimer":      "Este artículo es informativo y no reemplaza la evaluación de un profesional.",
  "fecha_revision":  "2026-05"
}
```

¿Hay campos adicionales necesarios? [ ]

---

### 3. ¿Dónde se almacenan los artículos?

```
Opción A — Archivos Markdown en el repositorio:
  docs/contenido/biblioteca/A-01.md
  docs/contenido/biblioteca/A-02.md
  ...
  → El backend los lee y los sirve estáticamente (o los incluye en el prompt)
  → Simple para el prototipo ✅

Opción B — Tabla en PostgreSQL:
  CREATE TABLE articulos_biblioteca (
    id_articulo    VARCHAR(5) PRIMARY KEY,
    titulo         TEXT,
    categoria      VARCHAR(50),
    contenido_md   TEXT,
    ...
  );
  → Permite filtrar, buscar y actualizar sin tocar código

¿Cuál es la estrategia para el prototipo? [ ]
```

---

### 4. ¿Quién redacta los artículos?

```
Los artículos requieren revisión clínica para garantizar que no contengan
información incorrecta sobre disfasia/afasia.

¿Se redactan manualmente? [ ]
¿Se asiste con el LLM (Gemini) usando fuentes bibliográficas como base? [ ]
¿Se requiere revisión de un logopeda antes de publicarlos? [ ]
```

---

### 5. Integración con el chatbot — Límite de tokens

```
Gemini 2.5 Flash tiene una ventana de contexto de 1M tokens.
Un artículo promedio de 500 palabras ≈ 650 tokens.
13 artículos × 650 tokens ≈ 8,450 tokens (muy dentro del límite).

¿Se incluyen todos los artículos en cada llamada al chatbot? [ ]
¿O solo los más relevantes según la pregunta del usuario? [ ]
(Para el prototipo: incluir todos es más simple)
```

---

### 6. Artículos prioritarios para el MVP

Para que el chatbot funcione desde la primera demo, ¿cuáles son los artículos mínimos?

| Prioridad | ID | Razón |
|---|---|---|
| 🔴 MVP | A-08 | Sin esto el chatbot no puede explicar qué es disfasia |
| 🔴 MVP | A-09 | Sin esto no puede explicar qué es afasia |
| 🔴 MVP | A-13 | Los padres siempre preguntan por qué se limitan las sesiones |
| 🔴 MVP | A-11 | Para explicar cómo funciona el diagnóstico |
| 🟡 Sprint 2 | A-01 | Señales de alerta más comunes |
| 🟡 Sprint 2 | A-04 | Estrategia de expansión (mencionada en el plan) |
| 🟢 Sprint 3 | Resto | Completar la biblioteca |

¿Está bien esta priorización? [ ]

---

## Preguntas abiertas

- [ ] ¿Los artículos tienen imágenes o son solo texto?
- [ ] ¿Se muestran en la app con un lector de artículos propio o se abren en el navegador?
- [ ] ¿El chatbot puede citar artículos de la biblioteca en sus respuestas? (ej. "Puedes leer más en el artículo A-04")
- [ ] ¿Los artículos están disponibles sin iniciar sesión (para discovery) o requieren autenticación?
- [ ] ¿Se necesita un disclaimer legal en cada artículo dado que habla de temas de salud?
