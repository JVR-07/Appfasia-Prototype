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

- **IPF (Índice de Precisión Fonológica)**: Usa `py-stringmatching` y el algoritmo Editex para comparar la transcripción obtenida vs. la palabra objetivo, normalizando acentos y mayúsculas. Devuelve un porcentaje 0-100.
- **LME (Longitud Media de Enunciado)**: Usa `spaCy` (`es_core_news_sm`) para extraer y contar morfemas de la respuesta, excluyendo signos de puntuación.
- **TRA (Tasa de Respuesta Auditiva)**: Clasifica la latencia en milisegundos (`FLUENT` <= 4s, `HINT` >= 5s, `TIMEOUT` >= 10s).

---

## 5. El Motor Diagnóstico

Ubicado en `diagnostic/evaluator.py`, ejecuta una máquina de estados estricta (Basal/Ceiling) con las siguientes fases (`DiagnosticPhase`):

1. **INITIALIZING**: Se calcula la edad y el nivel inicial (medio nivel por debajo del cronológico).
2. **AWAITING_BASAL**: El usuario debe responder 3 veces correctas seguidas en menos de 4s para establecer el nivel base.
3. **EXPLORING**: Se incrementa la dificultad. 2 aciertos avanzan de nivel, 1 fallo baja la dificultad dentro del mismo nivel.
4. **CEILING_DETECTED**: Tras 3 fallos o timeouts consecutivos, el diagnóstico termina.
5. **COMPLETED**: Se calcula el P(L0) base para la etapa de intervención.

> **Nota Clínica**: El motor diagnóstico incluye una "gracia" especial (`apply_first_timeout_grace()`). El primer _timeout_ absoluto de la prueba se perdona asumiendo nerviosismo infantil.
