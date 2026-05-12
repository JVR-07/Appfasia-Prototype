# **Plataforma Adaptativa e Inteligente para el Apoyo en Trastornos del Aprendizaje del Lenguaje (Appfasia)**

## **1. Planteamiento del Problema**

Los trastornos del lenguaje representan una dificultad significativa en el desarrollo comunicativo de las personas, afectando su desempeño académico, social y emocional. Entre estos trastornos destacan la disfasia, que se manifiesta en la infancia como una alteración en la adquisición del lenguaje, y la afasia, que implica la pérdida parcial o total del lenguaje debido a daño cerebral.

Uno de los principales problemas asociados es la falta de detección temprana, así como el desconocimiento por parte de padres, cuidadores y educadores, lo que retrasa la intervención adecuada. Además, los servicios especializados suelen ser limitados, costosos o poco accesibles, especialmente en contextos con menor acceso a atención profesional.

En este contexto, surge la necesidad de desarrollar herramientas tecnológicas accesibles que apoyen tanto la estimulación del lenguaje como la orientación educativa.

## **2. Objetivos del Proyecto**

**Objetivo General:** Desarrollar una plataforma digital web y móvil basada en inteligencia artificial generativa que funcione como asistente educativo interactivo para apoyar la estimulación del lenguaje y orientar a padres y cuidadores sobre trastornos del lenguaje.

**Objetivos Específicos:**

- Diseñar un asistente virtual tipo "amigo imaginario" que interactúe con usuarios infantiles.
- Implementar un algoritmo de evaluación adaptativa que determine el nivel real de competencia del usuario utilizando como base variables de entrada como la edad cronológica.
- Implementar actividades dinámicas que favorezcan el desarrollo del lenguaje.
- Integrar contenidos educativos sobre afasia y disfasia.
- Proporcionar herramientas de apoyo y orientación para padres y cuidadores.
- Generar retroalimentación personalizada basada en la interacción del usuario.
- Promover la detección temprana de posibles dificultades del lenguaje.

## **3. Arquitectura del Sistema: Lógica Adaptativa y de Aprendizaje**

Esta sección define el comportamiento inteligente de la plataforma para asegurar una experiencia completamente adaptada al usuario.

- **Evaluación Diagnóstica Dinámica:** El sistema solicitará un input inicial, como la edad del usuario. A partir de este dato, la plataforma presentará una prueba diagnóstica calibrada para el nivel esperado de esa edad. El motor de evaluación ajustará dinámicamente la dificultad de cada pregunta subsiguiente basándose en las respuestas (aumentando la dificultad si hay aciertos o disminuyéndola si hay errores) hasta encontrar el nivel base real del usuario. Esto permitirá identificar de forma precisa si el usuario presenta un rezago, va acorde a su edad o está adelantado.
- **Generación de Rutas de Aprendizaje:** Una vez detectado el nivel del usuario, el sistema generará de forma automática una serie de lecciones personalizadas enfocadas en regularizar su nivel de competencia. Estas rutas se estructurarán de manera gamificada e incluirán ejercicios de lectura, escritura, habla y comprensión.
- **Motor de Repetición Espaciada y Dosificación:** El sistema calculará automáticamente la frecuencia de repetición de cada lección o ejercicio según los resultados del usuario en la plataforma. Para evitar la sobreestimulación y la presión en el aprendizaje, el sistema limitará las lecciones diarias permitidas, fomentando que el usuario descanse y repase los conceptos en días posteriores para una mejor consolidación del conocimiento.

### **Clasificación y Naturaleza de la Inteligencia Artificial**

El motor de inferencia de la plataforma se define técnicamente como una IA Híbrida de Memoria Limitada. Esta arquitectura combina dos enfoques fundamentales para garantizar un equilibrio entre precisión clínica y adaptabilidad predictiva:

- **IA Simbólica (Sistema Experto Basado en Reglas):** Utilizada para codificar el conocimiento de expertos en logopedia (hitos de Brown, Bloom y Lahey) y asegurar el cumplimiento estricto de los umbrales de decisión, reglas de seguridad y protocolos de hardware.
- **IA Probabilística (Redes Bayesianas):** Implementada a través del modelo Bayesian Knowledge Tracing (BKT), el cual estima el estado latente de conocimiento del usuario a partir de sus interacciones observadas.
- **Memoria Limitada:** A diferencia de los sistemas reactivos, esta IA utiliza el historial del usuario ("Memoria") para ajustar la ruta de aprendizaje, permitiendo que las decisiones presentes estén informadas por el progreso acumulado y la evolución de las métricas clínicas (LME, IPF, TRA).

## **4. Módulos y Funcionalidades Principales**

El proyecto se desarrollará bajo un enfoque tecnológico-educativo centrado en el usuario. La plataforma se divide en dos módulos principales:

### **4.1 Asistente Educativo (Modo Niño / Usuario)**

- Interacción con un personaje virtual (amigo imaginario). Este avatar estará impulsado por IA, acompañará al niño durante su proceso e incluso participará de manera inmersiva en los minijuegos (por ejemplo, con dinámicas donde el usuario deba ayudar o salvar al avatar completando ejercicios de lenguaje).
- Conversaciones adaptadas al nivel del usuario.
- Juegos y ejercicios de lenguaje.
- Refuerzo positivo y motivacional.
- Generación dinámica de historias y actividades mediante IA.

### **4.2 Modo Padres / Cuidadores**

- Información clara sobre trastornos del lenguaje.
- Explicación de afasia y disfasia.
- Recomendaciones prácticas para el hogar.
- Chatbot Asistente con IA: Una herramienta interactiva para que el tutor pueda resolver dudas en tiempo real y obtener consejos sobre qué otras acciones tomar para ayudar en el desarrollo del menor.
- Seguimiento del progreso del usuario. Panel de analíticas que traduzca el progreso técnico a métricas comprensibles para los padres (ejemplo: "El usuario aprendió 30 palabras nuevas en una semana" o "El nivel de lectura ha mejorado el equivalente a dos años de edad cronológica en el último mes").
- Alertas sobre posibles señales de dificultad.

## **5. Justificación e Impacto Esperado**

El desarrollo del lenguaje es fundamental para la comunicación y el aprendizaje. La falta de herramientas accesibles que apoyen este proceso representa una barrera importante para muchas familias. Este proyecto se justifica en la necesidad de facilitar el acceso a recursos educativos sobre trastornos del lenguaje.

Asimismo, busca apoyar a padres sin formación especializada. Es importante destacar que la herramienta funcionará para complementar intervenciones del área de la Logopedia. Se aprovechará el potencial de la inteligencia artificial generativa para personalizar el aprendizaje. Además, la integración de tecnología en el ámbito educativo permite ampliar el alcance de las intervenciones, haciéndolas más inclusivas y accesibles.

**Resultados esperados (Impacto):**

- Desarrollo de una plataforma funcional web y móvil.
- Contribución a la detección temprana de dificultades del lenguaje.
- Mayor accesibilidad a herramientas educativas especializadas.
- Fortalecimiento del vínculo entre niños y cuidadores en el proceso de aprendizaje.
- Mejora en la estimulación del lenguaje en usuarios infantiles.
- Incremento en el conocimiento de padres y cuidadores sobre trastornos del lenguaje.
- Generación de experiencias educativas personalizadas mediante IA.
- Apoyo complementario a procesos terapéuticos.
- Innovación en el uso de inteligencia artificial aplicada a la educación y salud.

## **6. Rangos e Hitos de aprendizaje**

### **Edad: 0-1**

**Hitos:**

1. Repite sonidos que hacen otros.
2. Repite la misma sílaba 2 o 3 veces (ma, ma, ma).
3. Responde a los ademanes con ademanes.
4. Obedece una orden simple cuando va acompañada de ademanes.
5. Cuando se le dice "no", deja de hacer la actividad que está realizando, por lo menos momentáneamente, el 75% de las veces.
6. Responde a preguntas simples con una respuesta que no es oral.
7. Combina dos sílabas distintas en sus primeros intentos de hablar.
8. Imita los patrones de entonación de la voz de otros.
9. Emplea una sola palabra significativa para designar algún objeto o persona.
10. Hace sonidos como respuesta a otra persona que le habla.

### **Edad: 1-2**

**Hitos:**

1. Dice 5 palabras diferentes (puede usar la misma palabra para referirse a distintos objetos).
2. Pide "más".
3. Dice: "No hay más".
4. Obedece 3 órdenes diferentes pero simples que no van acompañadas de ademanes.
5. Puede "dar" o "mostrar" cuando se le pide.
6. Señala 12 objetos familiares cuando se le nombran.
7. Señala de 3 a 5 ilustraciones en un libro cuando se le nombran.
8. Señala 3 partes de su cuerpo.
9. Dice su propio nombre o apodo de cariño cuando se le pide.
10. Responde a la pregunta "¿Qué es ésto?" con el nombre del objeto.
11. Combina el uso de palabras y ademanes para manifestar sus deseos.
12. Nombra a otros 5 miembros de la familia incluyendo animales domésticos.
13. Nombra 4 juguetes.
14. Produce el sonido del animal o emplea el sonido para nombrar al animal (vaca es "muu”).
15. Pide algún tipo de alimento común nombrándolo cuando se le muestra (leche, galleta, pan).
16. Hace preguntas elevando la entonación de la voz al final de la palabra o frase.
17. Nombra 3 partes del cuerpo en una muñeca o en otra persona.
18. Responde a preguntas de alternativas si/no con respuesta afirmativa o negativa.

### **Edad: 2-3**

**Hitos:**

1. Combina sustantivos o adjetivos y sustantivos en frases de dos palabras ( pelota silla) (mi pelota).
2. Combina el sustantivo con el verbo en oraciones de dos palabras (papá va).
3. Emplea una palabra cuando necesita ir al baño.
4. Combina el verbo o sustantivo con "allí", "aquí", en expresiones de 2 palabras (silla aquí).
5. Combina 2 palabras para expresar pertenencia (auto papá).
6. Emplea "no" en su lenguaje.
7. Responde a la pregunta: "¿Qué está haciendo ...?" para referirse a actividades comunes.
8. Responde a preguntas de "¿Dónde?".
9. Nombra sonidos familiares del ambiente.
10. Entrega más de un objeto cuando se le piden, utilizando la fórmula plural (bloques).
11. Al hablar se refiere a sí mismo por su propio nombre.
12. Señala la ilustración de un objeto común cuyo uso se describe (llega hasta 10 objetos).
13. Indica su edad con los dedos.
14. Dice su sexo cuando se le pregunta.
15. Obedece a una serie de 2 mandatos relacionados.
16. Emplea el gerundio del verbo (hablando, corriendo).
17. Emplea formas regulares de plural (libro/libros).
18. Emplea constantemente algunas formas irregulares de verbos en el pasado (fue, hice, era).
19. Pregunta: "¿Qué es ésto (eso)?".
20. Controla el volumen de la voz el 90% de las veces.
21. Emplea "éste/ ésta" y "ese/ esa" al hablar.
22. Emplea "es" y "está" al construir oraciones simples (ésta es una pelota) (la pelota está aquí).
23. Dice: "yo, mí, mío", en lugar de su propio nombre.
24. Señala un objeto que "no es" (no es una pelota).
25. Responde a la pregunta "¿Quien?" dando un nombre.
26. Emplea la forma posesiva de los sustantivos (de papá).
27. Emplea los artículos: "el, la, los, las, un, una, unos, unas”, al hablar.
28. Emplea algunos nombres de grupos (juguete, animal, comida).
29. Usa con pocas equivocaciones los verbos "ser" "estar" y "tener" en el presente.
30. Describe los objetos diciendo que están "abiertos" o "cerrados".

### **Edad: 3-4**

**Hitos:**

1. Emplea correctamente "es" y "está" al iniciar una pregunta.
2. Presta atención durante 5 minutos mientras se le lee un cuento.
3. Lleva a cabo una serie de dos órdenes que no se relacionan.
4. Dice su nombre completo cuando se le pide. Responde a preguntas simples de "¿Cómo?".
5. Emplea los tiempos pasados de verbos regulares (saltó, saltaba).
6. Relata experiencias inmediatas.
7. Dice cómo se emplean objetos comunes.
8. Expresa acciones futuras empleando "ir a ", "tener que", "querer".
9. Cambia apropiadamente el orden de las palabras para formular preguntas (¿Puedo yo?) (¿Salta él?).
10. Usa el imperativo cuando pide un favor.
11. Cuenta 2 sucesos en el orden en que ocurrieron.

### **Edad: 4-5**

**Hitos:**

1. Obedece una serie de órdenes de 3 etapas.
2. Demuestra comprensión elemental de los verbos reflexivos y los usa al hablar.
3. Puede encontrar un par de objetos/ilustraciones cuando se le pide.
4. Emplea el futuro al hablar.
5. Emplea oraciones compuestas (Le pegué a la pelota y se rodó a la carretera).
6. Cuando se le pide puede encontrar la parte de "arriba" y la de "abajo" de los objetos.
7. Emplea el condicional (podría, sería, haría, etc. ) al hablar.
8. Puede nombrar cosas absurdas en una ilustración.
9. Emplea las palabras "hermana, hermano, abuelito, abuelita".
10. Dice la última palabra en analogías opuestas.
11. Relata un cuento conocido sin la ayuda de ilustraciones.
12. En una ilustración nombra el objeto que no pertenece a una clase determinada (uno que no es animal, etc.).
13. Dice si 2 palabras riman o no.
14. Dice oraciones complejas (Ella quiere que yo entre porque ...).
15. Dice si un sonido es "fuerte" o "suave".

### **Edad: 5-6**

**Hitos:**

1. Puede señalar algunos, muchos, varios.
2. Dice su dirección.
3. Dice el número de su teléfono.
4. Puede señalar el grupo que tiene más, menos o pocos.
5. Cuenta chistes sencillos.
6. Relata experiencias diarias.
7. Describe la ubicación o movimiento: a través de, lejos de, desde, hacia, encima.
8. Responde a la pregunta "¿Por qué?" con una explicación.
9. Pone en orden las partes y relata un cuento de 3 a 5 partes ordenadas en secuencia.
10. Define palabras.
11. Responde acertadamente al pedirle: "Dime lo opuesto de ..." Responde a la pregunta: "¿Qué pasa si...?" (dejas caer un huevo).
12. Emplea "ayer" y "mañana" correctamente.
13. Pregunta el significado de palabras nuevas o que no conoce.

### **Edad: 6-7**

**Hitos:**

1. Hacerse entender con facilidad.
2. Responder a preguntas más complejas contestando "sí" o "no".
3. Relatar un cuento una o varias veces y hablar sobre sucesos usando un orden lógico.
4. Expresar ideas con una variedad de oraciones completas.
5. Usar correctamente la mayoría de las partes de la oración (gramática).
6. Hacer y contestar preguntas (quién, qué, dónde, cuándo, por qué).
7. Atenerse al tema de la conversación y esperar su turno para hablar.
8. Dar instrucciones.
9. Iniciar conversaciones.
10. Recordar información.
11. Responder a instrucciones.
12. Seguir instrucciones de 2-3 pasos en secuencia.
13. Crear palabras que rimen.
14. Identificar todos los sonidos en las palabras cortas.
15. Combinar los sonidos para formar palabras.
16. Identificar las palabras habladas que correspondan a las palabras impresas.
17. Saber cómo se lee un libro (p. ej., lectura de izquierda a derecha y de arriba a abajo).
18. Identificar letras, palabras y oraciones.
19. Leer fonéticamente las palabras al leer.
20. Tener un vocabulario visual de 100 palabras comunes.
21. Leer con facilidad material apropiado al grado escolar.
22. Comprender lo leído.
23. Expresar ideas mediante la escritura.
24. Escribir con claridad en letra de molde.
25. Deletrear correctamente las palabras usadas con frecuencia.
26. Empezar las oraciones con letra mayúscula y usar puntuación final.
27. Escribir cuentos, anotaciones en un diario, o cartas y notas.

### **Edad: 7-8**

**Hitos:**

1. Seguir instrucciones orales de 3-4 pasos en secuencia.
2. Entender palabras que indican dirección (palabras que indican ubicación, espacio, tiempo).
3. Contestar correctamente preguntas sobre un cuento apropiado al grado escolar.
4. Hacerse entender con facilidad.
5. Responder a preguntas más complejas contestando "sí" o "no".
6. Hacer y contestar preguntas (p. ej., quién, qué, dónde, cuándo, por qué).
7. Usar estructuras cada vez más complejas en las oraciones.
8. Aclarar y explicar palabras e ideas.
9. Dar instrucciones de 3-4 pasos.
10. Usar el lenguaje oral para informar, persuadir y entretener.
11. Atenerse al tema, esperar su turno de hablar y usar contacto visual apropiado durante la conversación.
12. Iniciar y terminar de manera apropiada la conversación.
13. Dominar la lectura fónica/capacidad de reconocer los sonidos.
14. Asociar los fonemas, las sílabas, las palabras y las frases con sus formas escritas.
15. Reconocer muchas palabras a la vista.
16. Usar pistas de significado al leer (ej., ilustraciones, títulos y encabezados, información incluida en el cuento).
17. Releer y usar autocorrección cuando sea necesario.
18. Hallar información para contestar preguntas.
19. Explicar los elementos principales de un cuento (p. ej., idea principal, personajes principales, trama).
20. Usar sus propias experiencias para predecir y justificar lo que sucederá en los cuentos apropiados al grado escolar.
21. Leer, parafrasear/contar de nuevo un cuento en secuencia.
22. Leer con facilidad, ya sea en voz alta o en silencio, cuentos, poemas o textos dramáticos apropiados al grado escolar.
23. Leer de manera espontánea.
24. Identificar y usar patrones de ortografía en las palabras al leer.
25. Escribir legiblemente.
26. Usar una variedad de tipos de oraciones al escribir ensayos, poesías o narraciones cortas (ficción o didácticas).
27. Usar de manera apropiada las normas básicas de puntuación y de uso de mayúsculas.
28. Organizar la escritura para incluir principio, medio y final.
29. Deletrear correctamente las palabras usadas con frecuencia.
30. Progresar de una manera de deletrear inventiva (por ejemplo, según el sonido) a deletrear con mayor precisión.

### **Edad: 8-9**

**Hitos:**

1. Escuchar con atención en situaciones en grupo.
2. Entender el material apropiado al grado escolar.
3. Hablar con claridad y voz apropiada.
4. Hacer y contestar preguntas.
5. Participar en conversaciones y charlas en grupo.
6. Usar vocabulario apropiado al tema.
7. Atenerse al tema, usar contacto visual apropiado y esperar su turno de hablar en la conversación.
8. Resumir correctamente un cuento.
9. Explicar lo aprendido.
10. Demostrar dominio de la fonética básica.
11. Use destrezas de análisis de palabras al leer.
12. Usar pistas basadas en el contenido y en la estructura del lenguaje para entender lo leído.
13. Predecir y justificar lo que sucederá en un cuento, y comparar y contrastar cuentos.
14. Hacer y contestar preguntas sobre el material leído.
15. Usar la información adquirida para aprender sobre nuevos temas.
16. Leer con facilidad los libros apropiados al grado escolar (ficción o didácticos).
17. Releer y corregir errores si resultara necesario.
18. Planificar, organizar, revisar y hacer correcciones.
19. Incluir detalles al redactar.
20. Escribir cuentos, cartas, explicaciones sencillas e informes breves.
21. Deletrear correctamente palabras sencillas, hacer por su cuenta la corrección de la mayoría de los errores de ortografía y usar el diccionario para hacer correcciones ortográficas.
22. Escribir con claridad en letra cursiva.

###

### **Edad: 9-10**

**Hitos:**

1. Escuchar y entender la información presentada por los demás.
2. Formarse opiniones basadas en pruebas.
3. Escuchar con propósitos específicos.
4. Usar el vocabulario apropiado en la conversación.
5. Hacer uso eficaz del lenguaje con distintos propósitos.
6. Entender algo de lenguaje figurado (p. ej., "el bosque se extendía sobre...").
7. Participar en charlas de grupo.
8. Dar instrucciones precisas.
9. Resumir y replantear ideas.
10. Organizar la información con claridad.
11. Usar para el aprendizaje información y vocabulario pertinentes a la asignatura, como por ejemplo estudios sociales.
12. Dar presentaciones orales convincentes.
13. Leer con fines específicos.
14. Leer con facilidad libros apropiados al grado escolar.
15. Usar la información aprendida para entender nuevo material.
16. Seguir instrucciones escritas.
17. Tomar breves notas.
18. Relacionar la información aprendida a distintos temas.
19. Aprender el significado de nuevas palabras mediante el conocimiento de los múltiples significados, los sinónimos y los orígenes de las palabras.
20. Usar materiales de consulta, como los diccionarios.
21. Explicar el propósito y estilo del autor de una obra.
22. Leer y entender diversos tipos de literatura, incluyendo ficción, obras didácticas, ficción histórica y poesía.
23. Comparar y contrastar el contenido.
24. Hacer inferencias basadas en el contenido de un texto.
25. Parafrasear el contenido, incluyendo la idea principal y los detalles.
26. Escribir cuentos y explicaciones convincentes, incluyendo varios párrafos acerca de un mismo tema.
27. Crear un plan para la redacción, incluyendo principio, medio y final.
28. Organizar lo redactado para comunicar una idea central.
29. Revisar la versión final de lo redactado para hacer correcciones a la puntuación, la gramática y la ortografía.

### **Edad: 10-11**

**Hitos:**

1. Escuchar y sacar conclusiones en las actividades de aprendizaje de las asignaturas.
2. Hacer presentaciones orales preparadas de antemano que sean apropiadas a los oyentes.
3. Mantener contacto visual y utilizar expresiones faciales, voz y gestos apropiados durante las presentaciones orales.
4. Participar en los intercambios de ideas durante la clase en las distintas asignaturas
5. Resumir los puntos salientes de un tema.
6. Presentar información recopilada durante las actividades de grupo.
7. Leer con facilidad libros apropiados al grado escolar.
8. Aprender el significado de las palabras desconocidas mediante el conocimiento de las raíces de las palabras, los prefijos y los sufijos.
9. Organizar la información en orden de prioridad de acuerdo al propósito de la lectura.
10. Leer una variedad de formas literarias.
11. Describir el desarrollo de la trama y los personajes.
12. Describir las características de la poesía.
13. Analizar el lenguaje y estilo del autor de una obra.
14. Usar materiales de consulta para apoyar opiniones.
15. Redactar con diversos propósitos.
16. Usar el vocabulario con eficacia.
17. Variar la estructura de las oraciones.
18. Revisar lo redactado para determinar la claridad del estilo.
19. Hacer revisiones a la versión final de lo redactado.

## **7. Clasificación de la dificultad**

Para definir estos niveles, nos basamos en las etapas de adquisición del lenguaje de Brown y el modelo de Bloom y Lahey, agrupando los rangos de edad descritos en tus hitos.

- **Nivel 1: Descubrimiento Lingüístico (0 a 2 años):** Enfoque en atención conjunta, imitación vocal, onomatopeyas y vocabulario expresivo inicial (hasta 50-100 palabras).
- **Nivel 2: Estructuración Telegráfica y Expansión (2 a 4 años):** Enfoque en la combinación de 2 a 4 palabras, uso de verbos simples, plurales y comprensión de órdenes de dos pasos.
- **Nivel 3: Consolidación Sintáctica y Fonológica (4 a 6 años):** Enfoque en oraciones complejas, conjugación verbal (pasado/futuro), articulación de sinfones (consonantes dobles) y narración secuencial.
- **Nivel 4: Competencia Metalingüística Inicial (6 a 8 años):** Enfoque en la lectoescritura, conciencia fonológica avanzada, comprensión de lecturas cortas y seguimiento de instrucciones complejas.
- **Nivel 5: Razonamiento Pragmático y Abstracto (8 a 11 años):** Enfoque en lenguaje figurado, inferencias, gramática compleja, discursos y resolución de problemas mediante el lenguaje.

## **8. Tipos de actividades**

Las actividades se dividen por interacción de hardware y por objetivo clínico.

### **Clasificación por Hardware**

- **Voz/Micrófono (V-M):** Requiere que el usuario hable. Mide precisión fonética y latencia de respuesta.
- **Táctil/Arrastre (T-A):** Requiere pantalla táctil o ratón (Drag & Drop, trazos). Mide motricidad fina y asociación visual-motora.
- **Táctil/Selección (T-S):** Click simple o tap. Mide discriminación visual o auditiva.

### **Clasificación por Tipo de Ejercicio Clínico**

- **Denominación por Confrontación:** Se muestra imagen, el niño debe decir qué es (V-M).
- **Discriminación Auditiva:** El sistema reproduce un sonido/palabra, el niño selecciona la imagen correcta (T-S).
- **Categorización Semántica:** Agrupar elementos de una misma familia (ej. ropa, animales) (T-A).
- **Cierre Gramatical (Cloze):** Completar una oración oral o escrita (V-M o T-S).
- **Conciencia Fonológica:** Separar sílabas o identificar rimas (T-S o V-M).

### **Estructura General (Ejemplo):**

- **Tipo de ejercicio:** Discriminación Auditiva.
- **Clasificación por hardware:** T-S (Touch / Selección), Audio (Salida).
- **Dificultad:** Nivel 2 (2 a 4 años).
- **Calificación esperada:** Tiempo de respuesta menor a 5 segundos, 1 intento.
- **Calificación obtenida:** \[Variable dinámica: Ej. 4.2 seg, 1 intento \= 100%\].

## **9. Tipos de minijuegos**

Los minijuegos funcionan como refuerzo intermitente positivo (descansos activos) con la etiqueta interna `is_minigame = true`.

### Estos son algunos ejemplos

- **"Rescate del Avatar"** (Hardware: T-A, Dificultad: Adaptable). El avatar está atrapado. Para liberarlo, el niño debe arrastrar bloques (que forman una palabra o categoría) para construir un puente.

- **"Cazador de Burbujas Fonéticas"** (Hardware: V-M, Dificultad: Adaptable). Caen burbujas con imágenes. El niño debe gritar o pronunciar la sílaba objetivo (ej. "¡PA\!") para que el micrófono detecte el pico de audio y la burbuja explote.

- **"Memorama Auditivo"** (Hardware: T-S, Dificultad: Adaptable). Un juego de memoria donde no se emparejan dos imágenes, sino una imagen con una tarjeta que reproduce un sonido o sílaba.

## **10. Métricas de evaluación**

Estas métricas alimentarán el algoritmo adaptativo.

### **Modelado Probabilístico de Maestría (BKT)**

Para predecir si un usuario ha dominado realmente un hito de aprendizaje, el motor utiliza cuatro parámetros probabilísticos que permiten diferenciar entre un aprendizaje real, un acierto por azar o un error por distracción:

- **P(L0) \- Conocimiento Inicial:** Probabilidad de que el usuario ya domine el concepto antes de iniciar la lección (calibrado mediante la Evaluación Diagnóstica Inicial).
- **P(T) \- Probabilidad de Aprendizaje:** Probabilidad de que el usuario pase de un estado de "no conocimiento" a "maestría" tras realizar una actividad exitosa.
- **P(S) \- Probabilidad de Despiste (Slip):** Probabilidad de que el usuario, conociendo el concepto, cometa un error (ej. distracción o fallo técnico del micrófono).
- **P(G) \- Probabilidad de Adivinación (Guess):** Probabilidad de que el usuario acierte un ejercicio (especialmente en T-S o T-A) sin poseer el conocimiento real.

### **Métrica 1: LME (Longitud Media del Enunciado)**

- **Fórmula:** LME \= suma total de morfemas o palabras / número total de palabras evaluadas
- **Variables de entrada:** Texto transcrito por voz o escrito por el usuario.
- **Variables de salida:** Valor numérico continuo (ej. 2.5).
- **Justificación:** Es el estándar clínico mundial (propuesto por Roger Brown) para medir el desarrollo morfosintáctico. Un aumento en LME indica oraciones más largas y complejas.

### **Métrica 2: Índice de Precisión Fonológica (IPF)**

- **Fórmula:** IPF \= ( Fonemas pronunciados correctamente / Total de fonemas esperados) \* 100
- **Variables de entrada:** Audio del usuario procesado por Speech-to-Text.
- **Variables de salida:** Porcentaje de precisión (0% a 100%).
- **Justificación:** Permite identificar si el problema es articulatorio (dislalia) o fonológico, ayudando al sistema a decidir si repetir la lección con sonidos más simples.

### **Métrica 3: Tasa de Respuesta Auditiva (TRA)**

- **Fórmula: TRA \=** Tiempo(Click final) \- Tiempo(fin del estímulo sonoro)
- **Variables de entrada:** Timestamp del sistema.
- **Variables de salida:** Segundos/Milisegundos.
- **Justificación:** Evalúa la velocidad de procesamiento del lenguaje receptivo. Tiempos prolongados indican dificultad en la comprensión auditiva.

## **11. Umbrales de decisión**

### **Precisión Fonológica (IPF)**

El IPF mide la exactitud articulatoria procesando el audio del usuario . Este umbral determina el avance vertical (subir de nivel) o el ajuste de modalidad.  
**Umbral de Maestría (IPF \>= 80%):** El usuario pronuncia correctamente la mayoría de los fonemas esperados.

- **Decisión del motor:** Marcar el hito como "Dominado". Aumentar gradualmente la complejidad fonética (por ejemplo, pasar de sílabas simples a sinfones o consonantes dobles del Nivel 3).

**Umbral de Práctica (IPF entre 50% y 79%):** Hay errores consistentes, pero existe comprensión.

- **Decisión del motor:** Mantener la dificultad actual. Activar la "Estrategia de Expansión", programando repetición espaciada inteligente del mismo fonema en sesiones futuras.

**Umbral de Bloqueo/Frustración (IPF \< 50% en 3 intentos):** El usuario no logra articular correctamente el fonema.

- **Decisión del motor:** Intervención clínica. El sistema debe cambiar el tipo de hardware de Voz/Micrófono (V-M) a Táctil/Selección (T-S). Esto permite identificar si el problema es puramente articulatorio (dislalia) o si hay una falla en la discriminación auditiva.

### **Umbrales de Tasa de Respuesta Auditiva (TRA)**

El TRA mide la velocidad de procesamiento receptivo. Define qué tan automatizado tiene el niño el conocimiento.  
**Umbral de Fluidez (TRA \<= 4 segundos):** El tiempo de respuesta es óptimo, indicando procesamiento rápido.

- **Decisión del motor:** Validar aciertos. Si el IPF también es alto, el sistema puede "saltar" ejercicios redundantes para evitar el aburrimiento.

**Umbral de Latencia Cognitiva (TRA \> 5 segundos):** El usuario tarda en procesar el estímulo auditivo o visual.

- **Decisión del motor:** Si la respuesta final es correcta (IPF alto) pero el TRA es lento (\> 5s), el motor no debe subir la dificultad técnica de las palabras. Debe generar ejercicios de fluidez cronometrados en el nivel actual para mejorar la velocidad de asociación visual-motora o auditiva.

### **Umbrales de Longitud Media del Enunciado (LME)**

El LME evalúa el desarrollo morfosintáctico al procesar texto transcrito o escrito. Es el disparador principal para cambiar entre los Niveles de Competencia.  
**Umbral Telegráfico (LME entre 2 y 4):** Indica que el usuario está combinando palabras de forma básica.

- **Decisión del motor:** Activar actividades del Nivel 2 (Ej. Ejercicios de cierre gramatical simples y uso de verbos).

**Umbral de Transición Sintáctica (LME \> 4):** El usuario consistentemente produce enunciados más largos.

- **Decisión del motor:** Desbloquear el Nivel 3\. El motor de inferencia debe comenzar a exigir oraciones compuestas y el uso de tiempos verbales (pasado/futuro) en los ejercicios de Denominación por Confrontación.

### **Umbrales de Fatiga y Refuerzo (Control de Minijuegos)**

Para mantener el interés y evitar la sobreestimulación, el sistema debe monitorear el estado emocional indirectamente.  
**Umbral de Refuerzo Positivo:** Tras superar 3 ejercicios consecutivos con IPF \> 80% y TRA \< 4s.

- **Decisión del motor:** Inyectar un minijuego de consolidación. Cambiar la etiqueta interna a `is_minigame = true` y lanzar actividades como "Memorama Auditivo".

**Umbral de Rescate (Fatiga):** Tras 2 errores consecutivos (IPF bajo o silencio prolongado).

- **Decisión del motor:** Suspender temporalmente la evaluación formal. Iniciar un minijuego colaborativo como "Rescate del Avatar" (Táctil/Arrastre) , reduciendo la carga cognitiva y restaurando la motivación.

## **12. Reglas de Dosificación y Repetición Espaciada**

Para cumplir con tu objetivo de evitar la sobreestimulación, el sistema debe restringir el tiempo de uso basándose en las recomendaciones de la Academia Americana de Pediatría (AAP) y estructurar los repasos mediante un algoritmo de repaso espaciado.

### **Cálculo de la Competencia Actual (Memoria del Estudiante)**

Para mitigar el impacto de variables externas (cansancio, ruido ambiental o falta de atención temporal), el sistema no toma decisiones basadas únicamente en la última respuesta. Se utiliza una ponderación de Promedio Móvil Exponencial (EMA) para determinar el estado de competencia:  
**Estado actual \= (R0 \* 0.5) \+ (R\-1 \* 0.3) \+ (R\-2 \* 0.2)**

- **R0:** Rendimiento de la sesión actual.
- **R\-1:** Rendimiento de la sesión inmediata anterior.
- **R\-2:** Rendimiento de hace dos sesiones.

Este cálculo asegura que el sistema sea sensible a las mejoras recientes (sensibilidad del 50% al hoy), pero mantenga una "inercia" que proteja al niño de descensos de nivel frustrantes ante fallos aislados.

### **Límites Diarios (Dosificación)**

El "cierre de sesión" debe ser automático y dictado por el sistema, celebrando el esfuerzo del niño para que no lo sienta como un castigo.

| Nivel de Competencia | Rango de Edad | Límite de Sesión  | Estructura Recomendada por Día         |
| :------------------- | :------------ | :---------------- | :------------------------------------- |
| **Nivel 1 y 2**      | 0 a 4 años    | Máx. 10 \- 12 min | 3 a 4 ejercicios cortos \+ 1 minijuego |
| **Nivel 3**          | 4 a 6 años    | Máx. 15 \- 20 min | 5 a 7 ejercicios \+ 1 a 2 minijuegos   |
| **Niveles 4 y 5**    | 6 a 11 años   | Máx. 25 \- 30 min | 8 a 12 ejercicios \+ 2 minijuegos      |

### **Intervalos de Repetición Espaciada**

Cuando el niño supera un hito con un IPF \>= 80%, el motor no lo descarta. Lo programa en la cola de "Mantenimiento" con los siguientes intervalos:

1. **Revisión de Corto Plazo:** 24 horas después (Día siguiente).
2. **Consolidación:** 3 días después.
3. **Fijación:** 7 días después.
4. **Mantenimiento a Largo Plazo:** 21 días después.

Si en cualquiera de estas revisiones el IPF cae por debajo del 60%, el intervalo se reinicia al paso 1\.

### **Memoria del Estudiante (Corto vs. Largo Plazo)**

El motor de inferencia no debe ser impulsivo. Un niño puede tener un mal día por sueño o distracciones, y bajar su nivel abruptamente generaría frustración.

- **Regla de las 3 Sesiones (Tendencia Confirmada):** El sistema requiere 3 sesiones consecutivas con métricas por debajo del "Umbral de Práctica" (ej. IPF \< 50% o LME inferior al esperado) para ejecutar una reducción de Nivel (ej. bajar del Nivel 3 al Nivel 2 de forma permanente).
- **Ponderación del Historial (Promedio Móvil Exponencial):** Para calcular la competencia actual del niño, el motor le da más peso al presente que al pasado.
  - **Resultado de la sesión de hoy:** 50% del peso total.
  - **Resultado de la última sesión (ayer):** 30% del peso total.
  - **Resultado de hace dos sesiones:** 20% del peso total.
- **Justificación:** Esto permite que, si el niño tuvo una mejora repentina tras ir a terapia presencial, la aplicación lo detecte rápidamente y suba el nivel sin anclarse en los malos resultados de hace semanas.

## **13. Manejo de Excepciones y Ruido (Edge Cases)**

Las métricas clínicas se ven afectadas por la tecnología y la atención del niño. El motor debe tener protocolos estrictos para no penalizar falsamente.

### **Protocolo de Silencio (Timeout)**

En actividades de Voz/Micrófono (V-M), el silencio no debe contarse inmediatamente como un error fonológico.

- **A los 5 segundos (Latencia):** El asistente virtual (LLM) interviene con una ayuda semántica ("Pista: Es un animal que hace muuu").
- **A los 10 segundos (Timeout):** Se registra como "Intento nulo", no como "Error".
- **A los 3 Timeouts consecutivos:** El motor infiere un problema (fatiga severa, ruido ambiental o fallo del micrófono). Acción: El sistema bloquea temporalmente los ejercicios V-M y cambia automáticamente a Táctil/Arrastre (T-A).

### **Perfiles Inconsistentes (Lagunas Aisladas)**

Si un niño de 6 años resuelve perfectamente los problemas del Nivel 4 (Competencia Metalingüística), pero falla en nombrar colores simples del Nivel 2\.  
**Acción del Motor:** No se baja al niño al Nivel 2\. El motor clasifica al niño en Nivel 4, pero crea un "Ticket de Rezago". El sistema inyectará micro-ejercicios de Nivel 2 (colores) camuflados dentro de las actividades complejas del Nivel 4\.

### **Navegación en el Grafo de Conocimiento y Nodos Bloqueantes**

El Modelo de Dominio (la estructura de los 5 niveles y sus hitos) se implementa mediante una Base de Datos de Grafos. En este modelo, cada hito de aprendizaje es un Nodo y las dependencias pedagógicas son Aristas.

- **Nodos Bloqueantes:** Ciertos hitos fundamentales (ej. "imitación vocal" en Nivel 1 o "articulación de sinfones" en Nivel 3\) se marcan como bloqueantes. Si la probabilidad de maestría calculada por el BKT es \< 80%, el motor tiene restringido el avance hacia nodos de niveles superiores que tengan una dependencia directa con dicha habilidad.
- **Rutas de Recuperación:** Ante la detección de un "Ticket de Rezago" (dominio de niveles altos con fallas en niveles bajos), el motor utiliza el grafo para trazar una ruta de recuperación que inyecta automáticamente micro-ejercicios de los nodos faltantes de forma camuflada en la sesión actual.

## **14. Algoritmo de la Evaluación Diagnóstica Inicial**

Para cumplir con el objetivo de encontrar el nivel base real del usuario ajustando la dificultad en tiempo real, utilizaremos el concepto clínico de "Piso y Techo" (Basal and Ceiling).

- **Punto de Inicio:** El examen comienza sistemáticamente medio nivel por debajo de la edad cronológica ingresada. (Ej. Si el niño tiene 4 años, no empezamos con lo más difícil del Nivel 3, empezamos con conceptos del Nivel 2 para generar confianza).
- **Regla del Piso (Basal):** El sistema asume que el niño domina todo lo anterior a su nivel actual si logra 3 aciertos consecutivos con TRA rápido (\< 4s) al inicio de la prueba.
- **Regla del Techo (Ceiling \- Condición de Salida):** El examen termina automáticamente, sin importar cuántas preguntas falten, en el momento en que el niño acumula 3 errores o Timeouts consecutivos. El motor establece ese punto como su límite máximo actual.
- **Longitud máxima de la prueba:** Nunca debe exceder las 15 interacciones para evitar fatiga cognitiva en el primer contacto con la app.

## **15. Alcance de la documentación para padres**

Estructura de las entradas informativas para el módulo de cuidadores:

### **¿Mi hijo está tardando en hablar? Signos de alerta a los 2 años.**

- **Clasificación:** Detección Temprana / Alertas.
- **Contenido:** Explicación clara sobre la diferencia entre el ritmo individual de cada niño y los verdaderos focos rojos (ej. ausencia de balbuceo, no señalar objetos). Incluir infografía de "Cosas a observar".
- **Fuente Bibliográfica:** Centros para el Control y la Prevención de Enfermedades (CDC), Aprenda los signos. Reaccione pronto, 2022\.

### **Estrategia de Expansión: Cómo corregir sin frustrar.**

- **Clasificación:** Recomendaciones Prácticas / Hogar.
- **Contenido:** Técnica logopédica donde, si el niño dice "Auto corre", el padre no dice "así no se dice", sino que expande: "¡Sí\! El auto rojo corre muy rápido".
- **Fuente Bibliográfica:** Owens, R.E. (2020), Language Development: An Introduction.

## **16. Estructura de Plantillas Modulares por Nivel**

Esta sección detalla la arquitectura modular que permite al motor de inferencia generar miles de combinaciones de actividades a partir de unas pocas estructuras base. El objetivo es que el contenido no sea estático, sino que los "slots" de información se llenen dinámicamente según el nivel de competencia del usuario.

### **Jerarquía de Objetos (Arquitectura de Datos)**

Para que el sistema sea escalable, cada unidad de contenido se organiza en cuatro capas:

1. **Sesión (Contenedor Narrativo):** Agrupa de 2 a 3 lecciones bajo una temática visual (ej. "Sesión 1: El Mapamundi") . Define el tiempo máximo de uso (dosificación) según el rango de edad.
2. **Lección (Unidad Pedagógica):** Define el hito clínico a trabajar (ej. Conciencia de Categorías o Estructuración Sintáctica). Contiene las reglas de éxito (IPF \> 80%).
3. **Ejercicio (Unidad de Interacción):** La actividad técnica vinculada a un hardware específico (V-M, T-A, T-S).
4. **Minijuego (Refuerzo Intermitente):** Actividades con la etiqueta `is_minigame = true` que se activan al cumplir umbrales de refuerzo positivo.

### **Plantillas de Ejercicio (Adaptación por Nivel)**

Un mismo tipo de ejercicio cambia radicalmente su complejidad técnica y carga cognitiva dependiendo del nivel detectado por el examen inicial.  
**A. Plantilla: "El Nombrador" (Denominación por Confrontación)**

- **Hardware:** Voz/Micrófono (V-M).
- **Adaptación por Nivel:**
  - **Nivel 1-2:** Nombrar objetos simples o animales (ej. "Perro", "Vaca").
  - **Nivel 3:** Repetir palabras con fonemas complejos o sílabas trabadas (ej. "Piedra", "Puerta").
  - **Nivel 5:** Definir conceptos abstractos o describir ingredientes de un alimento complejo.

**B. Plantilla: "El Identificador" (Discriminación Auditiva/Visual)**

- **Hardware:** Táctil/Selección (T-S).
- **Adaptación por Nivel:**
  - **Nivel 1-2:** Tocar una parte del cuerpo en un avatar (instrucción de 1 paso).
  - **Nivel 3-4:** Identificar la imagen que "no pertenece" a una categoría o que rima con otra.
  - **Nivel 5:** Seleccionar la representación correcta de una emoción compleja o lenguaje figurado.

**C. Plantilla: "El Constructor" (Sintaxis y LME)**

- **Hardware:** Táctil/Arrastre (T-A).
- **Adaptación por Nivel:**
  - **Nivel 2:** Arrastrar palabras con la letra "M" hacia un objetivo.
  - **Nivel 3:** Ordenar bloques para formar oraciones simples (Sujeto \+ Verbo \+ Predicado).
  - **Nivel 4-5:** Completar párrafos o clasificar vehículos en un entorno complejo (estacionamiento).

### **Reglas de Inyección de Contenido**

Para que la personalización sea efectiva, el motor de inferencia aplica las siguientes reglas al seleccionar una plantilla:

- **Regla de No Repetición:** El sistema tiene prohibido repetir palabras o imágenes dentro de la misma sesión para evitar el aprendizaje por memorización simple.
- **Regla de Ajuste de TRA:** El tiempo límite para marcar un "Umbral de Fluidez" disminuye conforme aumenta el nivel (ej. 5s en Nivel 2 vs 3s en Nivel 5).
- **Regla de Modalidad:** Si el IPF es consistentemente bajo en plantillas V-M, el sistema inyecta automáticamente plantillas T-S para verificar la discriminación auditiva antes de retomar el habla.

### **Estructura de las Sesiones**

A continuación se definen ejemplos de lecciones estructuradas aplicando las variables que se requerirán:

**Sesión Ejemplo 1: Conciencia de Categorías**

- **Nombre de la lección:** Categorización_Basica_Animales_01
- **Dificultad:** Nivel 2 (2 a 4 años)
- **Número de ejercicios:** 3
- **Lista de ejercicios:**
  1. _Ejercicio 1 (T-S):_ Discriminación Auditiva. Escucha el sonido "Muuu" y selecciona la vaca entre 3 opciones.
  2. _Ejercicio 2 (V-M):_ Denominación. Aparece un perro. El sistema pide "¿Qué animal es?". El usuario debe pronunciarlo.
  3. _Ejercicio 3 (T-A):_ Arrastre. Llevar 3 animales a la imagen de una granja y 3 prendas de ropa a un armario.
- **Número de minijuegos:** 1
- **Lista de minijuegos:** _Minijuego 1 (T-S):_ "Explota las burbujas que tengan animalitos".
- **Promedio esperado:** Precisión mayor al 80%, TRA (Tiempo de respuesta) menor a 4 segundos por ejercicio.
- **Promedio obtenido:** \[Variable dinámica del sistema\].

**Sesión Ejemplo 2: Estructuración Sintáctica LME**

- **Nombre de la lección:** Construccion_Oraciones_Articulos_01
- **Dificultad:** Nivel 3 (4 a 6 años)
- **Número de ejercicios:** 2
- **Lista de ejercicios:**
  1. _Ejercicio 1 (T-A):_ Ordenamiento. Arrastrar bloques de palabras ("El", "perro", "corre") para formar la oración según una imagen.
  2. _Ejercicio 2 (V-M):_ Cierre gramatical. El asistente dice "La manzana es roja, pero el plátano es...". El niño debe decir "amarillo".
- **Número de minijuegos:** 1
- **Lista de minijuegos:** _Minijuego 1 (T-A):_ "Rescate del Avatar" arrastrando los bloques en orden correcto para construir el puente.
- **Promedio esperado:** 100% de precisión estructural.
- **Promedio obtenido:** \[Variable dinámica del sistema\].

## **17. Estrategia de Estructuración de Contenido: Enfoque Atómico y Relacional**

Para maximizar la capacidad adaptativa del motor de inferencia, el contenido no se almacena de forma rígida. Se utiliza un enfoque de tres capas que permite a la IA generar rutas de aprendizaje dinámicas basadas en la necesidad clínica inmediata del usuario.

### **Fase 1: El Diccionario de Recursos (Los Átomos)**

Esta capa contiene la "materia prima" del sistema. Cada palabra, frase o recurso multimedia está etiquetado con metadatos clínicos que permiten al motor de inferencia filtrar el contenido según el nivel de competencia y el hito objetivo.  
**Ejemplo de Estructura JSON (Recurso de Palabra):**  
`{`  
 `"id_recurso": "W_001",`  
 `"tipo": "palabra",`  
 `"texto": "Perro",`  
 `"nivel_sugerido": 1,`  
 `"fonema_objetivo": "rr",`  
 `"categoria_semantica": "animales",`  
 `"dificultad_articulacion": "alta",`  
 `"multimedia": {`  
 `"imagen_url": "assets/img/perro.png",`  
 `"audio_url": "assets/audio/perro.mp3"`  
 `},`  
 `"tags": ["domestico", "fonema_vibrante"]`  
`}`

### **Fase 2: Instanciación de Actividades (Las Moléculas)**

En esta capa, el sistema cruza las Plantillas Modulares (Sección 16) con los recursos del diccionario. En lugar de programar una actividad fija, el motor de inferencia realiza una consulta al diccionario para "llenar" los espacios de la plantilla en tiempo real.  
**Ejemplo de Estructura JSON (Instancia de Actividad):**  
`{`  
 `"id_actividad": "ACT_042",`  
 `"plantilla_base": "Plantilla_Nombrador",`  
 `"hardware_req": "V-M",`  
 `"objetivo_clinico": "IPF",`  
 `"configuracion": {`  
 `"items_a_evaluar": ["W_001", "W_045", "W_089"],`  
 `"umbral_exito_ipf": 80,`  
 `"tiempo_max_tra": 5.0`  
 `},`  
 `"feedback_asistente": {`  
 `"exito": "¡Increíble! Lo dijiste muy bien.",`  
 `"reintento": "Casi lo tienes, intenta decirlo un poco más despacio."`  
 `}`  
`}`

### **Fase 3: Estructura del Currículo (Los Organismos)**

Es la capa superior donde se define la lógica de navegación y la narrativa. Aquí es donde el motor de Bayesian Knowledge Tracing (BKT) y el Grafo de Conocimiento deciden qué lección es la más adecuada para el estado actual del estudiante.  
**Ejemplo de Estructura JSON (Estructura de Sesión):**  
`{`  
 `"id_sesion": "SES_01",`  
 `"titulo": "Exploradores en la Granja",`  
 `"narrativa": "Ayuda al avatar a encontrar a sus amigos los animales.",`  
 `"secuencia_logica": {`  
 `"leccion_1": {`  
 `"tipo": "Discriminacion_Auditiva",`  
 `"plantilla": "Plantilla_Identificador",`  
 `"filtros_recursos": { "categoria": "animales", "nivel": 1 }`  
 `},`  
 `"leccion_2": {`  
 `"tipo": "Denominacion_Confrontacion",`  
 `"plantilla": "Plantilla_Nombrador",`  
 `"filtros_recursos": { "categoria": "animales", "nivel": 2 }`  
 `}`  
 `},`  
 `"reglas_dosificacion": {`  
 `"duracion_estimada_min": 12,`  
 `"permite_minijuego": true`  
 `}`  
`}`

### **Implementación Técnica: Arquitectura de Datos Híbrida**

Para garantizar que el motor de inferencia sea capaz de procesar datos en milisegundos y mantener una Tasa de Respuesta Auditiva (TRA) fluida, la plataforma utilizará un esquema de almacenamiento especializado según el tipo de información:  
**A. Almacenamiento Relacional (SQL) para Recursos Atómicos**  
La "Fase 1: Los Átomos" se gestionará mediante tablas relacionales indexadas. Esto permite que la IA filtre recursos de manera instantánea según los requerimientos del ejercicio.

- **Uso:** Almacenar el diccionario maestro de palabras, frases y metadatos clínicos (fonemas, categorías, niveles).
- **Optimización:** Columnas específicas para fonema_objetivo, nivel_sugerido y id_categoria para evitar búsquedas lentas dentro de cadenas de texto.

**B. Base de Datos de Grafos para el Mapa de Conocimiento**  
La lógica de dependencia y navegación entre hitos de aprendizaje residirá en una base de datos de grafos.

- **Uso:** Mapear los Nodos (hitos de aprendizaje) y sus Aristas (requisitos pedagógicos y rutas de recuperación).
- **Beneficio:** Permite que el motor de Bayesian Knowledge Tracing (BKT) identifique "Nodos Bloqueantes" y calcule la ruta óptima de aprendizaje sin realizar consultas SQL complejas.

**C. Almacenamiento JSONB para Instancias y Logs**  
Se utilizará el formato JSON (o JSONB en PostgreSQL) únicamente para datos semi-estructurados y registros históricos que no requieren filtrado clínico frecuente.

- **Configuración de Plantillas:** Almacenar los esquemas de las plantillas de ejercicios (Sección 17) para que el motor pueda instanciarlas dinámicamente.
- **Historial de Sesión:** Guardar la sesión "armada" tal cual la vivió el usuario (JSON). Esto permite reconstruir la experiencia exacta del niño para análisis posterior o en caso de desconexión, protegiendo la Memoria del Estudiante.

## **18. Lógica de Retroalimentación Adaptativa del Avatar**

El asistente virtual ("amigo imaginario") no solo funciona como interfaz, sino como un agente de soporte emocional y pedagógico que ajusta su comportamiento comunicativo en tiempo real según el estado de maestría detectado por el motor de inferencia.

## **19. Intervención del Tutor en el Modelo Estudiante**

El modo padres permite realizar un "etiquetado manual" de la sesión que impacta directamente en el cálculo de la Memoria del Estudiante:

- **Etiquetado de Factores Externos:** El padre puede marcar una sesión con etiquetas como "Cansancio", "Distracción" o "Enfermedad".
- **Ajuste de Ponderación:** Cuando una sesión recibe estas etiquetas, el motor de inferencia reduce automáticamente el peso de R0 (el día de hoy) en la fórmula de competencia actual, evitando que un rendimiento bajo circunstancial degrade el nivel global del niño en el Grafo de Conocimiento.
- **Validación de Logros Externos:** El tutor puede informar al sistema si el niño ha mostrado avances en su entorno natural (fuera de la app), lo que permite al motor de inferencia programar pruebas de "salto de hito" para verificar si el usuario está listo para niveles superiores sin completar todos los ejercicios intermedios.
