# Algoritmo de Repetición Espaciada — Especificación Técnica
> 🔜 Pendiente · Prioridad: 🟡 Media

---

## Qué es este documento

Define la implementación técnica del sistema de repetición espaciada que programa revisiones periódicas de hitos ya dominados. El objetivo es consolidar el aprendizaje en la memoria a largo plazo.

---

## Contexto del proyecto

El plan (Sección 13) define los intervalos de revisión:
- **Revisión 1:** 24 horas después de dominar un hito
- **Revisión 2:** 3 días después
- **Revisión 3:** 7 días después
- **Revisión 4:** 21 días después (consolidación definitiva)

Cuando el niño pasa las 4 revisiones con éxito, el hito se considera **consolidado en memoria a largo plazo** y sale de la cola de repetición.

Lo que **falta definir** es cómo esto se integra técnicamente con el inicio de cada sesión y la selección de ejercicios.

---

## Qué hay que definir

### 1. Estructura de la cola en Redis

```
Clave Redis: spaced_rep:{child_id}
Tipo: Sorted Set (ZSET)
Score: timestamp UNIX de la próxima revisión
Member: id_hito
```

¿Es suficiente con un Sorted Set o se necesita más contexto por hito?

```
Alternativa con más datos — Hash por hito:
spaced_rep:{child_id}:{id_hito} → {
  proximo_review:  [ ] (timestamp)
  revision_num:    [ ] (1, 2, 3 o 4)
  ultimo_ipf:      [ ] (para ajustar el intervalo si la revisión falla)
}
```

### 2. Cuándo se añade un hito a la cola

```python
# Evento disparador: el BKT detecta P(maestría) >= umbral de dominio
# ¿Cuál es el umbral exacto de P(maestría) para considerar "dominado"?
UMBRAL_MAESTRIA = [ ]   # Sugerido: 0.85

# ¿Se añade el hito inmediatamente o al final de la sesión?
# [ ] Definir
```

### 3. Lógica al iniciar una sesión

Al llamar `POST /session/start`, el backend debe decidir cuántos ejercicios de revisión incluir vs. ejercicios nuevos:

```python
# ¿Cuántos hitos de revisión se pueden incluir por sesión?
MAX_REVISIONES_POR_SESION = [ ]   # Sugerido: 1-2

# ¿Con qué prioridad entran las revisiones en la sesión?
# - ¿Antes que los hitos nuevos?
# - ¿Al final?
# - ¿Intercalados?
PRIORIDAD_REVISIONES = [ ]

# ¿Qué pasa si hay 5 revisiones pendientes pero la sesión solo tiene 4 slots?
OVERFLOW_STRATEGY = [ ]
```

### 4. Qué pasa si la revisión falla

```python
# Si el niño falla una revisión (IPF < umbral):
# - ¿Se reinicia el contador de revisiones?
# - ¿Se programa una revisión adicional más próxima?
# - ¿Se activa el Ticket de Rezago?

ON_REVISION_FAIL = [ ]
```

### 5. Condición de graduación (salida de la cola)

```python
# ¿Cuándo se considera que un hito está "consolidado"?
# - ¿Después de las 4 revisiones exitosas?
# - ¿Después de la revisión 4 con IPF >= umbral?
CONDICION_GRADUACION = [ ]
```

### 6. Ajuste dinámico de intervalos

El plan sugiere que los intervalos pueden ajustarse según el rendimiento. ¿Se implementa para el prototipo?

```
Si IPF >= 90% en revisión → [ ] (¿aumentar el intervalo siguiente?)
Si IPF entre 70-80% en revisión → [ ] (¿mantener intervalo?)
Si IPF < 70% en revisión → [ ] (¿reducir el intervalo?)
```

---

## Preguntas abiertas

- [ ] ¿El sistema de repetición espaciada aplica también a hitos en diagnóstico o solo a los trabajados en sesiones regulares?
- [ ] ¿Las revisiones se muestran al niño de la misma forma que los ejercicios normales, o tienen alguna indicación especial?
- [ ] ¿El tutor ve en el dashboard qué hitos están "en revisión" vs. "en aprendizaje activo"?
- [ ] ¿El algoritmo de Leitner (cajas) es más apropiado que los intervalos fijos para el prototipo?
