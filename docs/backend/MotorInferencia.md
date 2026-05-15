# Motor de Inferencia (Inference Engine)

> **Documentación del Módulo**

El Motor de Inferencia es el núcleo cognitivo del backend de Appfasia. Es un motor puramente matemático y basado en reglas clínicas que evalúa las respuestas del niño, calcula probabilidades de aprendizaje y toma decisiones pedagógicas sobre qué acción tomar a continuación.

## 1. Arquitectura de Módulos

El código fuente se encuentra en `backend/inference_engine/` y está dividido en 6 submódulos principales, fuertemente tipados con Pydantic y Enum:

1. **`bkt/`**: Implementación de la fórmula Bayesiana (Bayesian Knowledge Tracing).
2. **`metrics/`**: Procesamiento de texto y audio para generar métricas clínicas (IPF, LME, TRA).
3. **`rules/`**: Algoritmos de decisión clínica basados en umbrales estáticos.
4. **`memory/`**: Cálculo de competencia a través del tiempo usando Promedios Móviles Exponenciales (EMA).
5. **`diagnostic/`**: Algoritmo de máquina de estados para la evaluación inicial (Basal y Ceiling).
6. **`decision/`**: El orquestador principal (`engine.py`) que agrega todos los submódulos.

---

## 2. Parámetros Bayesianos Clave

El sistema asume los siguientes parámetros estáticos (definidos en `bkt/engine.py`):

- **`P_TRANSIT (0.20)`**: Probabilidad de que el niño aprenda una habilidad después de practicarla.
- **`P_SLIP (0.10)`**: Probabilidad de que un niño falle aunque posea el conocimiento (por distracción o fallo del micrófono).
- **`P_MASTERY_THRESHOLD (0.80)`**: Umbral en el cual el sistema considera un hito como "dominado".
- **`P_GUESS`**: Dinámico según la plantilla:
  - `T-S (2 opciones)`: 0.50
  - `T-S (3 opciones)`: 0.33
  - `T-S (4 opciones)`: 0.25
  - `V-M` (Voz): 0.00 (no se puede adivinar una palabra hablada).

---

## 3. Flujo de Decisión Principal (`decision/engine.py`)

El orquestador toma métricas crudas (`RawMetrics`) y el estado actual (`BKTState`, `SessionContext`) y ejecuta una evaluación en cascada:

1. **Fallo de STT**: Si `is_low_confidence` es verdadero (confianza Azure STT < 0.70), la respuesta se ignora y la acción es `REPEAT`.
2. **Límite de Dosis**: Si se exceden los minutos máximos o número de ejercicios por nivel de edad, la sesión termina.
3. **Minijuegos**: Se revisan las rachas. 3 aciertos seguidos disparan "Recompensa". 2 fallos disparan "Rescate".
4. **Reglas de IP/TRA/LME**: Se clasifican las métricas contra los umbrales clínicos (`rules/`).
5. **Actualización BKT**: Se actualiza `p_mastery`.
6. **Memoria EMA**: Se calcula el EMA de las últimas 3 sesiones. Si las 3 están por debajo del umbral de práctica, se activa el `LEVEL_DOWN`.
7. **Salida**: Se genera un `EngineDecision` que instruye al frontend a `ADVANCE`, `REPEAT`, `MINIGAME`, etc.

---

## 4. Métricas Implementadas

### 4.1 Métricas Algorítmicas

- **IPF (Índice de Precisión Fonológica)**: Usa `py-stringmatching` y el algoritmo Editex para comparar la transcripción obtenida vs. la palabra objetivo, normalizando acentos y mayúsculas. Devuelve un porcentaje 0-100.
- **LME (Longitud Media de Enunciado)**: Usa `spaCy` (`es_core_news_sm`) para extraer y contar morfemas de la respuesta, excluyendo signos de puntuación.
- **TRA (Tasa de Respuesta Auditiva)**: Clasifica la latencia en milisegundos (`FLUENT` <= 4s, `HINT` >= 5s, `TIMEOUT` >= 10s).

### 4.2 Métrica Semántica con LLM — SEM

Para los niveles 3-5, las métricas algorítmicas no pueden evaluar la **calidad del contenido** de una respuesta oral. El módulo `metrics/llm_evaluator.py` usa **Gemini 2.5 Flash** para evaluar respuestas abiertas mediante rúbricas estructuradas.

**Flujo:**

```bash
Niño habla (V-M) → Azure STT → transcripción
                                    ↓
                    LLM Evaluator (Gemini 2.5 Flash)
                    Input:  transcripción + contexto del ejercicio + rúbrica
                    Output: SEMScore estructurado (0-100)
```

**Rúbricas disponibles:**

| Tipo de ejercicio            | Dimensiones evaluadas                         |
| ---------------------------- | --------------------------------------------- |
| Narración (Narrador)         | coherencia, vocabulario, estructura narrativa |
| Respuesta abierta (Pensador) | relevancia, profundidad, precisión factual    |

El LLM devuelve un JSON estructurado con scores por dimensión y un `score_global` ponderado. Si la llamada al LLM falla (rate limit, timeout), el ejercicio se marca como `SEM_UNAVAILABLE` y se repite sin penalización, análogo al manejo de `LOW_CONFIDENCE` en STT.

> **Nota:** El LLM **no reemplaza** IPF/LME/TRA — los complementa. IPF sigue midiendo _cómo_ pronuncia; SEM mide _qué_ dice.

---

## 5. Catálogo de Plantillas de Ejercicio

El sistema cuenta con **8 plantillas base**. Las plantillas A-C fueron diseñadas para los niveles 1-3 y las plantillas D-H extienden la evaluación a los niveles 4-5.

| #   | Plantilla         | Hardware | Niveles | Métricas                 | Usa LLM? |
| --- | ----------------- | -------- | ------- | ------------------------ | -------- |
| A   | **Nombrador**     | V-M      | 1-3     | IPF, TRA                 | No       |
| B   | **Identificador** | T-S      | 1-5     | Correcto/Incorrecto, TRA | No       |
| C   | **Constructor**   | T-A      | 2-5     | Orden correcto, TRA      | No       |
| D   | **Lector**        | V-M      | 4-5     | IPF (lectura), LME, TRA  | No       |
| E   | **Detective**     | T-S      | 4-5     | Correcto/Incorrecto, TRA | No       |
| F   | **Escritor**      | T-A      | 4-5     | Orden correcto, TRA      | No       |
| G   | **Narrador**      | V-M      | 3-5     | LME, TRA, SEM            | Sí       |
| H   | **Pensador**      | V-M      | 4-5     | LME, TRA, SEM            | Sí       |

### Plantillas Niveles 1-3

- **A. Nombrador** — Se muestra una imagen, el niño dice qué es. IPF compara la transcripción vs. la palabra objetivo.
- **B. Identificador** — Se reproduce un sonido/palabra, el niño selecciona la imagen correcta entre 3-4 opciones.
- **C. Constructor** — El niño arrastra bloques de palabras para formar oraciones ordenadas.

### Plantillas Niveles 4-5

- **D. Lector** — Se muestra texto escrito (oración o párrafo), el niño lo lee en voz alta. IPF compara la transcripción STT vs. el texto mostrado.
- **E. Detective** — Se lee un mini-texto, el niño responde preguntas de comprensión/inferencia con opciones múltiples. Incluye interpretación de lenguaje figurado.
- **F. Escritor** — El niño arrastra letras para deletrear palabras, u ordena oraciones/conectores para estructurar párrafos.
- **G. Narrador** — Se muestran imágenes en secuencia, el niño narra la historia. El LLM evalúa coherencia, vocabulario y estructura narrativa.
- **H. Pensador** — Se hace una pregunta abierta ("¿Por qué crees que...?", "Explica con tus palabras..."). El LLM evalúa relevancia, profundidad y precisión.

---

## 6. Alcance de Hitos del Prototipo

De los 224 hitos definidos en `PlanificacionProyecto.md`, el prototipo trabaja con **~200 hitos**. Se excluyen únicamente los hitos que requieren evaluación de habilidades físicas no digitalizables:

| Excluido                                   | Razón                                               |
| ------------------------------------------ | --------------------------------------------------- |
| Escribir en letra cursiva                  | Habilidad motriz fina no evaluable digitalmente     |
| Escribir legiblemente (caligrafía)         | Requiere análisis visual de escritura manuscrita    |
| Progresión de deletreo inventivo a preciso | Reemplazado por la plantilla Escritor (T-A digital) |

El catálogo completo de nodos y dependencias se encuentra en `docs/backend/GrafoConocimiento.md`.

---

## 7. El Motor Diagnóstico

Ubicado en `diagnostic/evaluator.py`, ejecuta una máquina de estados estricta (Basal/Ceiling) con las siguientes fases (`DiagnosticPhase`):

1. **INITIALIZING**: Se calcula la edad y el nivel inicial (medio nivel por debajo del cronológico).
2. **AWAITING_BASAL**: El usuario debe responder 3 veces correctas seguidas en menos de 4s para establecer el nivel base.
3. **EXPLORING**: Se incrementa la dificultad. 2 aciertos avanzan de nivel, 1 fallo baja la dificultad dentro del mismo nivel.
4. **CEILING_DETECTED**: Tras 3 fallos o timeouts consecutivos, el diagnóstico termina.
5. **COMPLETED**: Se calcula el P(L0) base para la etapa de intervención.

> **Nota Clínica**: El motor diagnóstico incluye una "gracia" especial (`apply_first_timeout_grace()`). El primer _timeout_ absoluto de la prueba se perdona asumiendo nerviosismo infantil.
