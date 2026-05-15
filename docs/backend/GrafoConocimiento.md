# Grafo de Conocimiento — ArcadeDB

> Catálogo de Hitos y Dependencias

---

## 1. Esquema del Grafo

### Nodo: `Hito`

| Atributo         | Tipo    | Descripción                                                                    |
| ---------------- | ------- | ------------------------------------------------------------------------------ |
| `id_hito`        | String  | Identificador único (ej. `H_N1_001`)                                           |
| `nombre`         | String  | Descripción clínica de la habilidad                                            |
| `nivel`          | Integer | Nivel de competencia (1-5)                                                     |
| `rango_edad_min` | Integer | Edad mínima esperada en meses                                                  |
| `rango_edad_max` | Integer | Edad máxima esperada en meses                                                  |
| `dimension`      | String  | `expresivo`, `comprensivo`, `fonologico`, `lectura`, `pragmatico`, `semantico` |
| `es_bloqueante`  | Boolean | `true` si es un requisito indispensable para avanzar                           |
| `orden_interno`  | Integer | Secuencia sugerida dentro del nivel                                            |

### Aristas

- `(A)-[:REQUIERE_DE {peso: 1.0}]->(B)`: A debe estar dominado antes de evaluar B (Condición lógica AND).
- `(A)-[:PRECEDE_A]->(B)`: Orden pedagógico natural, pero no estricto.
- `(A)-[:RUTA_ALTERNATIVA]->(B)`: Usada en la generación de Tickets de Rezago.
- `(A)-[:REFUERZA]->(B)`: Relación temática o semántica.

---

## 2. Catálogo de Hitos (~200 Nodos)

> **Nota sobre exclusiones:** Se omitieron ~24 hitos de los niveles 4 y 5 relacionados puramente con habilidades motoras o caligrafía (ej. "escribir en cursiva") que no son digitalizables. Hitos redundantes han sido consolidados bajo una única competencia (ej. redacción de diferentes tipos de texto).

### Nivel 1: Descubrimiento Lingüístico (0-2 años) — 28 hitos

| ID       | Nombre                                  | Rango Edad | Dimensión   | Bloqueante | Depende de |
| -------- | --------------------------------------- | ---------- | ----------- | ---------- | ---------- |
| H_N1_001 | Repite sonidos que hacen otros          | 0-12m      | expresivo   | Sí         | -          |
| H_N1_002 | Repite la misma sílaba 2 o 3 veces      | 0-12m      | fonologico  | No         | H_N1_001   |
| H_N1_003 | Responde a ademanes con ademanes        | 0-12m      | pragmatico  | No         | -          |
| H_N1_004 | Obedece una orden simple con ademanes   | 0-12m      | comprensivo | Sí         | -          |
| H_N1_005 | Detiene actividad al escuchar "no"      | 0-12m      | comprensivo | No         | -          |
| H_N1_006 | Responde a preguntas simples sin hablar | 0-12m      | comprensivo | No         | H_N1_004   |
| H_N1_007 | Combina dos sílabas distintas           | 0-12m      | fonologico  | Sí         | H_N1_002   |
| H_N1_008 | Imita patrones de entonación            | 0-12m      | expresivo   | No         | H_N1_001   |
| H_N1_009 | Emplea una palabra significativa        | 0-12m      | expresivo   | Sí         | H_N1_007   |
| H_N1_010 | Hace sonidos en respuesta a habla       | 0-12m      | pragmatico  | No         | -          |
| H_N1_011 | Dice 5 palabras diferentes              | 12-24m     | expresivo   | Sí         | H_N1_009   |
| H_N1_012 | Pide "más"                              | 12-24m     | pragmatico  | No         | H_N1_009   |
| H_N1_013 | Dice "No hay más"                       | 12-24m     | expresivo   | No         | H_N1_011   |
| H_N1_014 | Obedece 3 órdenes simples sin ademanes  | 12-24m     | comprensivo | Sí         | H_N1_004   |
| H_N1_015 | "Dar" o "mostrar" cuando se le pide     | 12-24m     | comprensivo | No         | H_N1_004   |
| H_N1_016 | Señala 12 objetos familiares nombrados  | 12-24m     | comprensivo | Sí         | H_N1_014   |
| H_N1_017 | Señala 3-5 ilustraciones en un libro    | 12-24m     | comprensivo | No         | H_N1_016   |
| H_N1_018 | Señala 3 partes de su cuerpo            | 12-24m     | semantico   | No         | H_N1_014   |
| H_N1_019 | Dice su propio nombre                   | 12-24m     | expresivo   | No         | H_N1_009   |
| H_N1_020 | Responde "¿Qué es esto?" con nombre     | 12-24m     | expresivo   | Sí         | H_N1_011   |
| H_N1_021 | Combina palabras y ademanes             | 12-24m     | pragmatico  | No         | H_N1_011   |
| H_N1_022 | Nombra 5 miembros de familia/mascotas   | 12-24m     | semantico   | No         | H_N1_011   |
| H_N1_023 | Nombra 4 juguetes                       | 12-24m     | semantico   | No         | H_N1_011   |
| H_N1_024 | Produce/emplea sonidos de animales      | 12-24m     | expresivo   | No         | H_N1_007   |
| H_N1_025 | Pide alimento común nombrándolo         | 12-24m     | pragmatico  | No         | H_N1_011   |
| H_N1_026 | Preguntas elevando la entonación        | 12-24m     | expresivo   | No         | H_N1_008   |
| H_N1_027 | Nombra 3 partes en una muñeca           | 12-24m     | semantico   | No         | H_N1_018   |
| H_N1_028 | Responde sí/no a alternativas           | 12-24m     | comprensivo | Sí         | H_N1_006   |

### Nivel 2: Estructuración Telegráfica (2-4 años) — 41 hitos

| ID       | Nombre                                   | Rango Edad | Dimensión   | Bloqueante | Depende de |
| -------- | ---------------------------------------- | ---------- | ----------- | ---------- | ---------- |
| H_N2_001 | Combina sustantivo/adjetivo (2 palabras) | 24-36m     | expresivo   | Sí         | H_N1_011   |
| H_N2_002 | Combina sustantivo+verbo                 | 24-36m     | expresivo   | Sí         | H_N2_001   |
| H_N2_003 | Palabra para ir al baño                  | 24-36m     | pragmatico  | No         | H_N1_009   |
| H_N2_004 | Expresiones con allí/aquí                | 24-36m     | semantico   | No         | H_N2_001   |
| H_N2_005 | Expresa pertenencia (auto papá)          | 24-36m     | semantico   | No         | H_N2_001   |
| H_N2_006 | Emplea "no" al hablar                    | 24-36m     | expresivo   | Sí         | H_N1_011   |
| H_N2_007 | Responde "¿Qué está haciendo?"           | 24-36m     | comprensivo | Sí         | H_N1_020   |
| H_N2_008 | Responde preguntas "¿Dónde?"             | 24-36m     | comprensivo | No         | H_N2_007   |
| H_N2_009 | Nombra sonidos familiares                | 24-36m     | expresivo   | No         | H_N1_020   |
| H_N2_010 | Entrega más de un objeto (plurales)      | 24-36m     | comprensivo | Sí         | H_N1_014   |
| H_N2_011 | Se refiere a sí mismo por nombre         | 24-36m     | expresivo   | No         | H_N1_019   |
| H_N2_012 | Señala objeto descrito por uso           | 24-36m     | comprensivo | Sí         | H_N1_016   |
| H_N2_013 | Indica edad con los dedos                | 24-36m     | pragmatico  | No         | -          |
| H_N2_014 | Dice su sexo                             | 24-36m     | expresivo   | No         | H_N2_011   |
| H_N2_015 | Obedece 2 mandatos relacionados          | 24-36m     | comprensivo | Sí         | H_N1_014   |
| H_N2_016 | Emplea gerundio (corriendo)              | 24-36m     | expresivo   | No         | H_N2_002   |
| H_N2_017 | Emplea plurales regulares                | 24-36m     | expresivo   | Sí         | H_N2_001   |
| H_N2_018 | Verbos irregulares en pasado             | 24-36m     | expresivo   | No         | H_N2_002   |
| H_N2_019 | Pregunta "¿Qué es esto?"                 | 24-36m     | pragmatico  | No         | H_N2_001   |
| H_N2_020 | Controla volumen de voz                  | 24-36m     | pragmatico  | No         | -          |
| H_N2_021 | Emplea este/ese                          | 24-36m     | expresivo   | No         | H_N2_001   |
| H_N2_022 | Emplea "es" y "está" simples             | 24-36m     | expresivo   | Sí         | H_N2_002   |
| H_N2_023 | Dice yo/mí/mío                           | 24-36m     | expresivo   | Sí         | H_N2_011   |
| H_N2_024 | Señala objeto que "no es"                | 24-36m     | comprensivo | No         | H_N2_006   |
| H_N2_025 | Responde "¿Quién?"                       | 24-36m     | comprensivo | No         | H_N2_007   |
| H_N2_026 | Forma posesiva de sustantivos            | 24-36m     | expresivo   | No         | H_N2_005   |
| H_N2_027 | Emplea artículos (el, la, un)            | 24-36m     | expresivo   | Sí         | H_N2_001   |
| H_N2_028 | Nombres de grupos (animal, juguete)      | 24-36m     | semantico   | No         | H_N1_016   |
| H_N2_029 | Verbos ser/estar/tener                   | 24-36m     | expresivo   | Sí         | H_N2_022   |
| H_N2_030 | Describe abierto/cerrado                 | 24-36m     | semantico   | No         | H_N2_001   |
| H_N2_031 | Es/está al inicio de pregunta            | 36-48m     | expresivo   | No         | H_N2_029   |
| H_N2_032 | Atención a cuento (5 mins)               | 36-48m     | comprensivo | Sí         | -          |
| H_N2_033 | 2 órdenes no relacionadas                | 36-48m     | comprensivo | Sí         | H_N2_015   |
| H_N2_034 | Nombre completo                          | 36-48m     | expresivo   | No         | H_N2_011   |
| H_N2_035 | Responde "¿Cómo?"                        | 36-48m     | comprensivo | No         | H_N2_025   |
| H_N2_036 | Pasado de verbos regulares               | 36-48m     | expresivo   | Sí         | H_N2_018   |
| H_N2_037 | Relata experiencias inmediatas           | 36-48m     | pragmatico  | Sí         | H_N2_002   |
| H_N2_038 | Dice cómo se emplean objetos             | 36-48m     | semantico   | No         | H_N2_012   |
| H_N2_039 | Acciones futuras (ir a, querer)          | 36-48m     | expresivo   | Sí         | H_N2_029   |
| H_N2_040 | Usa imperativo                           | 36-48m     | pragmatico  | No         | -          |
| H_N2_041 | Cuenta 2 sucesos en orden                | 36-48m     | pragmatico  | Sí         | H_N2_037   |

### Nivel 3: Consolidación Sintáctica (4-6 años) — 28 hitos

| ID       | Nombre                               | Rango Edad | Dimensión   | Bloqueante | Depende de |
| -------- | ------------------------------------ | ---------- | ----------- | ---------- | ---------- |
| H_N3_001 | Ordenes de 3 etapas                  | 48-60m     | comprensivo | Sí         | H_N2_033   |
| H_N3_002 | Verbos reflexivos                    | 48-60m     | expresivo   | No         | H_N2_029   |
| H_N3_003 | Encontrar pares                      | 48-60m     | semantico   | No         | -          |
| H_N3_004 | Emplea el futuro simple              | 48-60m     | expresivo   | Sí         | H_N2_039   |
| H_N3_005 | Oraciones compuestas (con "y")       | 48-60m     | expresivo   | Sí         | H_N2_036   |
| H_N3_006 | Conceptos arriba/abajo               | 48-60m     | semantico   | No         | H_N2_008   |
| H_N3_007 | Emplea condicional (podría)          | 48-60m     | expresivo   | No         | H_N3_004   |
| H_N3_008 | Cosas absurdas en ilustración        | 48-60m     | comprensivo | No         | -          |
| H_N3_009 | Vocabulario familia extendida        | 48-60m     | semantico   | No         | -          |
| H_N3_010 | Analogías opuestas simples           | 48-60m     | semantico   | Sí         | -          |
| H_N3_011 | Relata cuento conocido sin imágenes  | 48-60m     | pragmatico  | Sí         | H_N2_041   |
| H_N3_012 | Identifica elemento excluido         | 48-60m     | semantico   | Sí         | H_N2_028   |
| H_N3_013 | Detecta rimas                        | 48-60m     | fonologico  | Sí         | -          |
| H_N3_014 | Oraciones complejas (con "porque")   | 48-60m     | expresivo   | Sí         | H_N3_005   |
| H_N3_015 | Sonido fuerte/suave                  | 48-60m     | fonologico  | No         | -          |
| H_N3_016 | Conceptos cantidad (algunos, muchos) | 60-72m     | semantico   | No         | -          |
| H_N3_017 | Dice su dirección                    | 60-72m     | expresivo   | No         | -          |
| H_N3_018 | Dice número de teléfono              | 60-72m     | expresivo   | No         | -          |
| H_N3_019 | Identifica más/menos                 | 60-72m     | semantico   | No         | H_N3_016   |
| H_N3_020 | Cuenta chistes sencillos             | 60-72m     | pragmatico  | No         | H_N3_008   |
| H_N3_021 | Relata experiencias diarias          | 60-72m     | pragmatico  | Sí         | H_N3_011   |
| H_N3_022 | Ubicación espacial compleja          | 60-72m     | semantico   | No         | H_N3_006   |
| H_N3_023 | Responde "¿Por qué?" con explicación | 60-72m     | expresivo   | Sí         | H_N3_014   |
| H_N3_024 | Secuencia lógica 3-5 partes          | 60-72m     | pragmatico  | Sí         | H_N3_011   |
| H_N3_025 | Define palabras                      | 60-72m     | semantico   | Sí         | H_N3_010   |
| H_N3_026 | Identifica opuestos                  | 60-72m     | semantico   | No         | H_N3_010   |
| H_N3_027 | Usa ayer/mañana                      | 60-72m     | semantico   | Sí         | H_N3_004   |
| H_N3_028 | Pregunta por palabras nuevas         | 60-72m     | pragmatico  | No         | H_N2_019   |

### Nivel 4: Competencia Metalingüística (6-8 años) — 48 hitos consolidados

| ID       | Nombre                                  | Rango Edad | Dimensión   | Bloqueante | Depende de |
| -------- | --------------------------------------- | ---------- | ----------- | ---------- | ---------- |
| H_N4_001 | Hacerse entender con facilidad          | 72-96m     | expresivo   | Sí         | H_N3_024   |
| H_N4_002 | Oraciones completas variadas            | 72-96m     | expresivo   | Sí         | H_N3_014   |
| H_N4_003 | Correcta gramática general              | 72-96m     | expresivo   | Sí         | H_N4_002   |
| H_N4_004 | Preguntas complejas (quién, por qué)    | 72-96m     | expresivo   | No         | H_N3_023   |
| H_N4_005 | Atenerse al tema y turnos               | 72-96m     | pragmatico  | No         | -          |
| H_N4_006 | Dar instrucciones precisas              | 72-96m     | pragmatico  | No         | H_N3_001   |
| H_N4_007 | Iniciar conversaciones                  | 72-96m     | pragmatico  | No         | H_N4_005   |
| H_N4_008 | Recordar información                    | 72-96m     | comprensivo | Sí         | H_N3_024   |
| H_N4_009 | Instrucciones 3-4 pasos en secuencia    | 72-96m     | comprensivo | Sí         | H_N3_001   |
| H_N4_010 | Crear palabras que rimen                | 72-96m     | fonologico  | Sí         | H_N3_013   |
| H_N4_011 | Identificar sonidos en palabras         | 72-96m     | fonologico  | Sí         | H_N3_015   |
| H_N4_012 | Combinar sonidos para formar palabras   | 72-96m     | fonologico  | Sí         | H_N4_011   |
| H_N4_013 | Asociar palabras habladas e impresas    | 72-96m     | lectura     | Sí         | H_N4_012   |
| H_N4_014 | Conocimiento de dirección de lectura    | 72-96m     | lectura     | No         | -          |
| H_N4_015 | Identificar letras, palabras, oraciones | 72-96m     | lectura     | Sí         | H_N4_013   |
| H_N4_016 | Lectura fonética básica                 | 72-96m     | lectura     | Sí         | H_N4_015   |
| H_N4_017 | Vocabulario visual de 100 palabras      | 72-96m     | lectura     | Sí         | H_N4_016   |
| H_N4_018 | Comprensión de lectura básica           | 72-96m     | comprensivo | Sí         | H_N4_016   |
| H_N4_019 | Escribir con mayúsculas y puntuación    | 72-96m     | expresivo   | No         | H_N4_015   |
| H_N4_020 | Deletreo frecuente correcto             | 72-96m     | fonologico  | No         | H_N4_012   |
| H_N4_021 | Redacción básica (cuentos, notas)       | 72-96m     | expresivo   | No         | H_N4_019   |
| H_N4_022 | Direcciones espaciales y tiempo         | 84-96m     | semantico   | No         | H_N3_027   |
| H_N4_023 | Responder preguntas de un cuento        | 84-96m     | comprensivo | Sí         | H_N4_018   |
| H_N4_024 | Estructuras complejas en oraciones      | 84-96m     | expresivo   | No         | H_N4_003   |
| H_N4_025 | Aclarar y explicar palabras e ideas     | 84-96m     | semantico   | Sí         | H_N3_025   |
| H_N4_026 | Persuadir y entretener oralmente        | 84-96m     | pragmatico  | No         | H_N4_021   |
| H_N4_027 | Contacto visual y cierre de charla      | 84-96m     | pragmatico  | No         | H_N4_005   |
| H_N4_028 | Dominio fonético y de sílabas           | 84-96m     | fonologico  | Sí         | H_N4_012   |
| H_N4_029 | Pistas de significado (títulos, fotos)  | 84-96m     | comprensivo | No         | H_N4_018   |
| H_N4_030 | Autocorrección al leer                  | 84-96m     | lectura     | No         | H_N4_016   |
| H_N4_031 | Hallar información específica           | 84-96m     | comprensivo | No         | H_N4_018   |
| H_N4_032 | Explicar trama, personajes, idea base   | 84-96m     | semantico   | Sí         | H_N4_023   |
| H_N4_033 | Predecir y justificar sucesos           | 84-96m     | comprensivo | No         | H_N4_032   |
| H_N4_034 | Parafrasear cuento en secuencia         | 84-96m     | pragmatico  | Sí         | H_N4_023   |
| H_N4_035 | Lectura fluida en voz alta o silencio   | 84-96m     | lectura     | No         | H_N4_016   |
| H_N4_036 | Identificar patrones de ortografía      | 84-96m     | fonologico  | No         | H_N4_020   |
| H_N4_037 | Estructura escrita (inicio, medio, fin) | 84-96m     | expresivo   | Sí         | H_N4_021   |

### Nivel 5: Razonamiento Abstracto (8-11 años) — 54 hitos consolidados

| ID       | Nombre                                     | Rango Edad | Dimensión   | Bloqueante | Depende de |
| -------- | ------------------------------------------ | ---------- | ----------- | ---------- | ---------- |
| H_N5_001 | Participar en charlas grupales             | 96-132m    | pragmatico  | No         | H_N4_027   |
| H_N5_002 | Resumir correctamente un cuento            | 96-132m    | comprensivo | Sí         | H_N4_034   |
| H_N5_003 | Explicar lo aprendido de texto             | 96-132m    | comprensivo | No         | H_N5_002   |
| H_N5_004 | Pistas de contexto para significado        | 96-132m    | semantico   | Sí         | H_N4_029   |
| H_N5_005 | Comparar y contrastar historias            | 96-132m    | comprensivo | No         | H_N4_032   |
| H_N5_006 | Planificar, organizar y revisar textos     | 96-132m    | expresivo   | No         | H_N4_037   |
| H_N5_007 | Explicaciones sencillas e informes         | 96-132m    | expresivo   | No         | H_N5_006   |
| H_N5_008 | Formarse opiniones con pruebas             | 108-132m   | pragmatico  | Sí         | H_N5_005   |
| H_N5_009 | Entender lenguaje figurado (metáforas)     | 108-132m   | semantico   | Sí         | H_N5_004   |
| H_N5_010 | Dar presentaciones orales convincentes     | 108-132m   | pragmatico  | No         | H_N5_008   |
| H_N5_011 | Sintetizar múltiples significados/raíces   | 108-132m   | semantico   | Sí         | H_N5_004   |
| H_N5_012 | Relacionar información a temas nuevos      | 108-132m   | comprensivo | No         | H_N5_003   |
| H_N5_013 | Propósito y estilo de un autor             | 108-132m   | comprensivo | No         | H_N5_005   |
| H_N5_014 | Entender ficción, poesía e histórico       | 108-132m   | comprensivo | No         | H_N5_013   |
| H_N5_015 | Inferencias basadas en un texto            | 108-132m   | comprensivo | Sí         | H_N5_005   |
| H_N5_016 | Escribir ensayos de varios párrafos        | 108-132m   | expresivo   | No         | H_N5_007   |
| H_N5_017 | Extraer conclusiones en aprendizaje        | 120-132m   | comprensivo | Sí         | H_N5_015   |
| H_N5_018 | Expresión y voz al presentar en público    | 120-132m   | pragmatico  | No         | H_N5_010   |
| H_N5_019 | Organizar información por prioridad        | 120-132m   | comprensivo | No         | H_N5_012   |
| H_N5_020 | Describir desarrollo de trama y personajes | 120-132m   | comprensivo | No         | H_N5_013   |
| H_N5_021 | Análisis de la poesía                      | 120-132m   | comprensivo | No         | H_N5_014   |
| H_N5_022 | Redacción con diversos propósitos          | 120-132m   | expresivo   | No         | H_N5_016   |

---

## 3. Integración con `navigator.py`

Las consultas Cypher interactúan con este esquema.
Por ejemplo, para obtener el siguiente nodo óptimo:

```cypher
MATCH (cand:Hito)
WHERE NOT cand.id_hito IN $mastered
OPTIONAL MATCH (prereq:Hito)-[:REQUIERE_DE]->(cand)
WITH cand, collect(prereq.id_hito) AS reqs
WHERE all(r IN reqs WHERE r IN $mastered)
RETURN cand
ORDER BY cand.nivel ASC, cand.orden_interno ASC
LIMIT 1
```
