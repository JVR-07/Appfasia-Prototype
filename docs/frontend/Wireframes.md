# Wireframes y Especificación de Pantallas — Appfasia
> Documento vivo · Ir completando cada pantalla conforme se diseñe

---

## Cómo usar este documento

Cada pantalla tiene la misma estructura de secciones. Completa cada campo con la información de diseño. Los campos marcados con `[ ]` están vacíos y esperan definición.

**Estructura de cada pantalla:**
- **Descripción** — Para qué sirve esta pantalla
- **Ruta** — URL en el router de React
- **Condición de entrada** — Cuándo/cómo llega el usuario aquí
- **Componentes UI** — Qué elementos visuales tiene
- **Estados** — Variaciones de la pantalla (carga, error, vacío, etc.)
- **Navegación** — A dónde se puede ir desde aquí
- **Endpoint(s) API** — Qué llamadas hace al backend
- **Notas / preguntas abiertas** — Decisiones pendientes

---

## Modo Niño

---

### 🧒 N-01 · Selección de Perfil de Niño

**Descripción:** [ ]

**Ruta:** `/child-select`

**Condición de entrada:** [ ]

**Componentes UI:**
- [ ]

**Estados:**
- `single_child` — Solo un perfil registrado: [ ]
- `multiple_children` — Varios perfiles: [ ]
- `no_children` — Sin perfiles creados aún: [ ]

**Navegación:**
- Al seleccionar un perfil → [ ]
- Botón "Añadir niño" → [ ]

**Endpoints API:**
- `GET /children`

**Notas / preguntas abiertas:**
- [ ]

---

### 🧪 N-02 · Introducción al Diagnóstico

**Descripción:** [ ]

**Ruta:** `/diagnostic/intro`

**Condición de entrada:** Primera vez que el niño usa la app (sin diagnóstico completado)

**Componentes UI:**
- [ ]

**Estados:**
- `ready` — Pantalla de bienvenida lista: [ ]

**Navegación:**
- Botón "¡Empezar!" → N-03

**Endpoints API:**
- `POST /diagnostic/start`

**Notas / preguntas abiertas:**
- [ ] ¿El avatar explica qué va a pasar?
- [ ] ¿Se necesita confirmación del tutor antes de empezar?

---

### 🧪 N-03 · Ejercicio Diagnóstico

**Descripción:** [ ]

**Ruta:** `/diagnostic/exercise`

**Condición de entrada:** Diagnóstico en curso (`session_diag_id` activo en la sesión)

**Componentes UI:**
- [ ] Avatar + instrucción de voz
- [ ] Imagen/audio del estímulo
- [ ] 3 opciones táctiles con imagen
- [ ] Indicador de progreso (ej. "3 de 15")

**Estados:**
- `presenting` — Avatar dando la instrucción: [ ]
- `awaiting` — Esperando toque del niño: [ ]
- `evaluating` — Enviando respuesta al backend: [ ]
- `correct` — Feedback positivo: [ ]
- `incorrect` — Feedback neutro (sin decir "mal"): [ ]

**Navegación:**
- Última interacción → N-04

**Endpoints API:**
- `POST /diagnostic/response`

**Notas / preguntas abiertas:**
- [ ] ¿Cómo se ve el feedback de error? ¿Animación del avatar?

---

### 🎉 N-04 · Resultado del Diagnóstico

**Descripción:** [ ]

**Ruta:** `/diagnostic/result`

**Condición de entrada:** `estado: "COMPLETADO"` recibido del backend

**Componentes UI:**
- [ ] Avatar celebrando
- [ ] Mensaje de felicitación
- [ ] (Opcional) indicador del nivel detectado en lenguaje infantil

**Estados:**
- `celebration` — Pantalla de festejo: [ ]

**Navegación:**
- Botón de continuar → N-05 (inicio de sesión)

**Endpoints API:**
- (Usa el resultado devuelto por `POST /diagnostic/response` en el último paso)

**Notas / preguntas abiertas:**
- [ ] ¿Se muestra el nivel detectado al niño o solo al tutor?

---

### 🏠 N-05 · Inicio de Sesión

**Descripción:** [ ]

**Ruta:** `/session/start`

**Condición de entrada:** Diagnóstico completado y sesión no iniciada hoy

**Componentes UI:**
- [ ] Avatar saludando
- [ ] Barra de progreso de la racha de días
- [ ] Botón "¡Juguemos!"

**Estados:**
- `ready` — Sesión disponible: [ ]
- `limit_reached` — Ya se jugó hoy → redirige a N-13

**Navegación:**
- "¡Juguemos!" → N-06 / N-07 / N-08 (según plantilla del primer ejercicio)

**Endpoints API:**
- `POST /session/start`

**Notas / preguntas abiertas:**
- [ ] ¿Se muestra cuántos ejercicios faltan?

---

### 🎤 N-06 · Ejercicio — Nombrador (V-M)

**Descripción:** [ ]

**Ruta:** `/session/exercise` (la plantilla se determina por el JSON recibido)

**Condición de entrada:** `plantilla: "Nombrador"` en la respuesta del backend

**Componentes UI:**
- [ ] Imagen grande del recurso (sin texto)
- [ ] Avatar con instrucción de voz
- [ ] Botón de micrófono (grande, centrado, con estados visuales)
- [ ] Indicador de tiempo restante (TRA)

**Estados del micrófono:**
- `idle` — Esperando que el niño pulse: [ ]
- `recording` — Grabando (animación de onda de audio): [ ]
- `processing` — Enviando al backend: [ ]

**Estados de la pantalla:**
- `presenting` — Avatar da instrucción: [ ]
- `awaiting` — Niño puede responder: [ ]
- `hint_5s` — Avatar da pista semántica: [ ]
- `timeout_10s` — Intento nulo registrado: [ ]
- `success` — IPF >= umbral: [ ]
- `retry` — IPF < umbral: [ ]

**Navegación:**
- Respuesta evaluada → siguiente ejercicio (mismo componente, nuevo JSON) o minijuego o fin de sesión

**Endpoints API:**
- `POST /session/response`

**Notas / preguntas abiertas:**
- [ ] ¿El botón de micrófono es un tap o tap-and-hold?
- [ ] ¿Cómo se visualiza el feedback de IPF bajo sin frustrar al niño?

---

### 👆 N-07 · Ejercicio — Identificador (T-S)

**Descripción:** [ ]

**Ruta:** `/session/exercise` (determinada por JSON)

**Condición de entrada:** `plantilla: "Identificador"` en la respuesta del backend

**Componentes UI:**
- [ ] Instrucción de audio (reproducción automática)
- [ ] 3 opciones visuales (imágenes grandes, táctiles)
- [ ] Avatar en esquina con instrucción verbal
- [ ] Indicador de TRA (opcional, no visible para el niño)

**Estados:**
- `presenting` — Audio del estímulo reproduciéndose: [ ]
- `awaiting` — Esperando toque: [ ]
- `correct` — Opción correcta seleccionada: [ ]
- `incorrect` — Opción incorrecta: [ ]
- `timeout` — Sin respuesta en TRA máximo: [ ]

**Navegación:**
- Igual que N-06

**Endpoints API:**
- `POST /session/response`

**Notas / preguntas abiertas:**
- [ ] ¿Las opciones se ordenan aleatoriamente en cada render?
- [ ] ¿Animación de "shake" en opción incorrecta?

---

### 🧩 N-08 · Ejercicio — Constructor (T-A)

**Descripción:** [ ]

**Ruta:** `/session/exercise` (determinada por JSON)

**Condición de entrada:** `plantilla: "Constructor"` en la respuesta del backend

**Componentes UI:**
- [ ] Imagen de escena (descripción visual)
- [ ] Bloques de palabras arrastrables (zona de origen)
- [ ] Zona de destino (la "oración" en construcción)
- [ ] Botón "Verificar" (activo solo cuando todos los bloques están colocados)
- [ ] Avatar con instrucción

**Estados:**
- `presenting` — Avatar dando instrucción: [ ]
- `building` — Niño arrastrando bloques: [ ]
- `verifying` — Enviando al backend: [ ]
- `correct` — Orden correcto: [ ]
- `incorrect` — Orden incorrecto (highlight del error): [ ]

**Navegación:**
- Igual que N-06

**Endpoints API:**
- `POST /session/response`

**Notas / preguntas abiertas:**
- [ ] ¿Los bloques vuelven a la zona de origen si se suelta en lugar inválido?
- [ ] ¿Se permite borrar y reordenar antes de verificar?

---

### 🎮 N-09 · Minijuego — Rescate del Avatar

**Descripción:** [ ]

**Ruta:** `/session/minigame/rescate`

**Condición de entrada:** `accion: "MINIJUEGO"`, `tipo_minijuego: "Rescate_Avatar"` en respuesta del motor

**Componentes UI:**
- [ ]

**Estados:**
- [ ]

**Navegación:**
- Al completar → siguiente ejercicio o fin de sesión

**Endpoints API:**
- `POST /session/response` (con `tipo_respuesta: "minijuego_completado"`)

**Notas / preguntas abiertas:**
- [ ] ¿Cuál es exactamente la mecánica de juego?
- [ ] ¿Tiene un contador de tiempo?

---

### 🫧 N-10 · Minijuego — Cazador de Burbujas Fonéticas

**Descripción:** [ ]

**Ruta:** `/session/minigame/burbujas`

**Condición de entrada:** `tipo_minijuego: "Cazador_Burbujas"`

**Componentes UI:**
- [ ]

**Estados:**
- [ ]

**Navegación:**
- Al completar → siguiente ejercicio o fin de sesión

**Endpoints API:**
- `POST /session/response`

**Notas / preguntas abiertas:**
- [ ] ¿Las burbujas contienen imágenes, palabras escritas o audio?
- [ ] ¿El niño usa el micrófono o toca la pantalla?

---

### 🃏 N-11 · Minijuego — Memorama Auditivo

**Descripción:** [ ]

**Ruta:** `/session/minigame/memorama`

**Condición de entrada:** `tipo_minijuego: "Memorama_Auditivo"`

**Componentes UI:**
- [ ] Tablero de tarjetas (pares imagen + audio)
- [ ]

**Estados:**
- [ ]

**Navegación:**
- Al completar → siguiente ejercicio o fin de sesión

**Endpoints API:**
- `POST /session/response`

**Notas / preguntas abiertas:**
- [ ] ¿Cuántos pares tiene el tablero?

---

### 🏆 N-12 · Sesión Completada

**Descripción:** [ ]

**Ruta:** `/session/complete`

**Condición de entrada:** `estado_sesion: "COMPLETADA"` en respuesta del motor

**Componentes UI:**
- [ ] Avatar festejando (animación)
- [ ] Resumen: ejercicios completados, hitos dominados hoy
- [ ] Racha de días (estrellas / fuego)
- [ ] Botón "¡Hasta mañana!"

**Estados:**
- `celebration` — Pantalla principal: [ ]
- `new_milestone` — Se dominó un hito nuevo (variación especial): [ ]

**Navegación:**
- "¡Hasta mañana!" → N-01 (selección de perfil)

**Endpoints API:**
- (Usa el payload de `POST /session/response` del último ejercicio)

**Notas / preguntas abiertas:**
- [ ]

---

### ⏱️ N-13 · Límite Diario Alcanzado (Dosificación)

**Descripción:** [ ]

**Ruta:** `/session/limit`

**Condición de entrada:** Error `SESSION_LIMIT_REACHED` en `POST /session/start`

**Componentes UI:**
- [ ] Avatar con mensaje de pausa positiva
- [ ] Hora de la próxima sesión disponible
- [ ] Botón "¡Hasta mañana!"

**Estados:**
- `today_done` — Sesión de hoy completada: [ ]
- `already_done` — Intento de segunda sesión: [ ]

**Navegación:**
- → N-01

**Endpoints API:**
- (Respuesta 403 de `POST /session/start`)

**Notas / preguntas abiertas:**
- [ ]

---

## Modo Padres / Tutores

---

### 👤 P-01 · Login / Registro de Tutor

**Descripción:** [ ]

**Ruta:** `/auth/login` y `/auth/register`

**Condición de entrada:** Usuario no autenticado (sin JWT válido)

**Componentes UI:**
- [ ] Formulario de email + contraseña
- [ ] Toggle Login / Registrarse
- [ ] (Registro) campo de nombre completo

**Estados:**
- `login` — Formulario de acceso: [ ]
- `register` — Formulario de registro: [ ]
- `loading` — Enviando credenciales: [ ]
- `error` — Credenciales incorrectas: [ ]

**Navegación:**
- Login exitoso → P-02
- Registro exitoso → P-03 (crear primer perfil de niño)

**Endpoints API:**
- `POST /auth/login`
- `POST /auth/register`

**Notas / preguntas abiertas:**
- [ ] ¿"¿Olvidaste tu contraseña?" para el prototipo?

---

### 👨‍👩‍👧 P-02 · Gestión de Perfiles (Tutores)

**Descripción:** [ ]

**Ruta:** `/parent/children`

**Condición de entrada:** Tutor autenticado en modo padres

**Componentes UI:**
- [ ] Lista de perfiles de niños registrados
- [ ] Botón "Añadir niño"
- [ ] Acceso al dashboard de cada niño

**Estados:**
- `has_children` — Al menos un perfil: [ ]
- `empty` — Sin perfiles creados: [ ]

**Navegación:**
- Seleccionar niño → P-03
- "Añadir niño" → Modal o página de creación

**Endpoints API:**
- `GET /children`
- `POST /children`

**Notas / preguntas abiertas:**
- [ ]

---

### 📊 P-03 · Dashboard de Progreso

**Descripción:** [ ]

**Ruta:** `/parent/progress/:child_id`

**Condición de entrada:** Tutor selecciona un perfil de niño

**Componentes UI:**
- [ ] Nombre del niño + nivel actual
- [ ] Racha de días
- [ ] Resumen de la semana (sesiones, minutos, palabras)
- [ ] Métricas traducidas a lenguaje humano
- [ ] Alertas / recomendaciones del motor
- [ ] Acceso al historial de sesiones
- [ ] Acceso al chatbot

**Estados:**
- `active` — Datos disponibles: [ ]
- `no_data` — Niño registrado pero sin sesiones: [ ]
- `loading` — Cargando datos: [ ]

**Navegación:**
- "Ver historial" → P-04
- "Hablar con el asistente" → P-06
- "Reportar avance externo" → Modal P-07

**Endpoints API:**
- `GET /progress/:child_id`

**Notas / preguntas abiertas:**
- [ ] ¿Gráfico de progreso de IPF por semana?
- [ ] ¿Se muestra el nivel en equivalencia de edad (ej. "nivel de un niño de 3 años y 2 meses")?

---

### 📋 P-04 · Historial de Sesiones

**Descripción:** [ ]

**Ruta:** `/parent/progress/:child_id/sessions`

**Condición de entrada:** Desde el dashboard P-03

**Componentes UI:**
- [ ] Lista de sesiones ordenadas por fecha
- [ ] Para cada sesión: fecha, duración, ejercicios, IPF promedio, etiqueta del tutor
- [ ] Filtros (fecha, etiqueta)

**Estados:**
- `populated` — Con historial: [ ]
- `empty` — Sin sesiones registradas: [ ]

**Navegación:**
- Tocar una sesión → P-05
- Volver → P-03

**Endpoints API:**
- `GET /progress/:child_id/sessions`

**Notas / preguntas abiertas:**
- [ ]

---

### 🔍 P-05 · Detalle de Sesión

**Descripción:** [ ]

**Ruta:** `/parent/progress/:child_id/sessions/:session_id`

**Condición de entrada:** Desde el historial P-04

**Componentes UI:**
- [ ] Resumen de la sesión (métricas)
- [ ] Lista de ejercicios realizados
- [ ] Selector de etiqueta (Cansancio / Distracción / Enfermedad / Otro)
- [ ] Campo de nota opcional

**Estados:**
- `unlabeled` — Sin etiqueta del tutor: [ ]
- `labeled` — Con etiqueta aplicada: [ ]

**Navegación:**
- Volver → P-04

**Endpoints API:**
- `POST /progress/:child_id/sessions/:session_id/label`

**Notas / preguntas abiertas:**
- [ ] ¿Se puede quitar o cambiar una etiqueta ya aplicada?

---

### 💬 P-06 · Chatbot Asistente para Padres

**Descripción:** [ ]

**Ruta:** `/parent/chatbot`

**Condición de entrada:** Desde el dashboard P-03

**Componentes UI:**
- [ ] Interfaz de chat (burbujas usuario / asistente)
- [ ] Campo de texto con botón de envío
- [ ] Indicador de escritura del asistente
- [ ] Preguntas frecuentes sugeridas (chips)

**Estados:**
- `idle` — Listo para recibir mensaje: [ ]
- `loading` — Esperando respuesta del LLM: [ ]
- `error` — Error de red o LLM: [ ]

**Navegación:**
- Volver → P-03

**Endpoints API:**
- `POST /chatbot/message`

**Notas / preguntas abiertas:**
- [ ] ¿Se persiste el historial del chat entre sesiones?
- [ ] ¿Hay un disclaimer "No reemplaza a un profesional"?

---

### 🌟 P-07 · Reportar Avance Externo (Modal)

**Descripción:** [ ]

**Ruta:** Modal sobre P-03

**Condición de entrada:** Tutor hace clic en "Reportar avance"

**Componentes UI:**
- [ ] Campo de texto (descripción del avance observado)
- [ ] Selector de hito relacionado (opcional)
- [ ] Botón "Guardar"

**Estados:**
- `open` — Modal visible: [ ]
- `submitting` — Enviando: [ ]
- `success` — Confirmación de recepción: [ ]

**Navegación:**
- Cerrar modal → P-03

**Endpoints API:**
- `POST /progress/:child_id/external-advance`

**Notas / preguntas abiertas:**
- [ ] ¿Se muestra una lista de hitos para seleccionar o es texto libre?

---

## Sistema de Diseño (Transversal)

> Completar antes de implementar cualquier pantalla

### 🎨 Paleta de Colores

| Uso | Color (HEX) | Nombre |
|---|---|---|
| Primario | `[ ]` | [ ] |
| Secundario | `[ ]` | [ ] |
| Fondo Modo Niño | `[ ]` | [ ] |
| Fondo Modo Padres | `[ ]` | [ ] |
| Éxito | `[ ]` | [ ] |
| Alerta / Error | `[ ]` | [ ] |
| Texto principal | `[ ]` | [ ] |
| Texto secundario | `[ ]` | [ ] |

### ✏️ Tipografía

| Uso | Fuente | Tamaño | Peso |
|---|---|---|---|
| Títulos (Modo Niño) | `[ ]` | `[ ]` | `[ ]` |
| Texto instrucción Avatar | `[ ]` | `[ ]` | `[ ]` |
| Texto UI Padres | `[ ]` | `[ ]` | `[ ]` |
| Botones | `[ ]` | `[ ]` | `[ ]` |

### 🤖 Estados del Avatar

| Estado | Descripción | Animación |
|---|---|---|
| Neutro / Idle | [ ] | [ ] |
| Hablando | [ ] | [ ] |
| Celebrando | [ ] | [ ] |
| Dando pista | [ ] | [ ] |
| Esperando | [ ] | [ ] |
| Preocupado (soporte) | [ ] | [ ] |

### 📐 Espaciado y Grid

- Grid base: `[ ]`
- Border radius botones: `[ ]`
- Tamaño mínimo área táctil (niños): `[ ]` (recomendado: ≥ 48×48px)
