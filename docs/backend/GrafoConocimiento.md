# Grafo de Conocimiento — ArcadeDB
> 🔜 Pendiente · Prioridad: 🔴 Alta

---

## Qué es este documento

Define el esquema del grafo de conocimiento en ArcadeDB y el proceso para poblar la base de datos con todos los **hitos de aprendizaje** (nodos) y sus **dependencias pedagógicas** (aristas). Sin este grafo, el Decision Engine no puede calcular rutas de aprendizaje ni detectar hitos bloqueantes.

---

## Contexto del proyecto

El plan del proyecto (Secciones 6 y 7) define ~200 hitos de aprendizaje distribuidos en 9 rangos de edad (desde 0-6 meses hasta 8-11 años), organizados en dimensiones como lenguaje expresivo, comprensión, conciencia fonológica, etc.

El motor de inferencia usa ArcadeDB para responder preguntas como:
- ¿Cuál es el siguiente hito que debe trabajar este niño?
- ¿Qué hitos están bloqueados porque dependen de uno no dominado?
- ¿Existe una ruta alternativa si el niño está bloqueado en un nodo difícil?

El driver utilizado es el `neo4j` Python driver conectándose por protocolo BOLT al puerto 7687 de ArcadeDB.

---

## Qué hay que definir

### 1. Esquema de Nodos (Hitos)

Definir los atributos de cada nodo `Hito` en el grafo:

```
Nodo: Hito {
  id_hito:        [ ] (ej. "H_N2_003")
  nombre:         [ ] (ej. "Uso de sustantivos plurales")
  descripcion:    [ ]
  nivel:          [ ] (1-5)
  rango_edad_min: [ ] (meses)
  rango_edad_max: [ ] (meses)
  dimension:      [ ] (ej. "expresivo", "comprensivo", "fonologico")
  dificultad:     [ ] (alta / media / baja)
  fonema_asociado:[ ] (opcional)
}
```

### 2. Esquema de Aristas (Dependencias)

Definir los tipos de relaciones entre hitos:

```
Arista: REQUIERE_DE
  → "El hito A solo puede trabajarse si el hito B está dominado"

Arista: PRECEDE_A
  → "El hito A es el paso anterior natural al hito B"

Arista: RUTA_ALTERNATIVA
  → "Si el hito A está bloqueado, el hito B es un camino alternativo"

Arista: REFUERZA
  → "Practicar el hito A también fortalece indirectamente el hito B"
```

¿Hay otros tipos de relaciones necesarios? [ ]

### 3. Catálogo completo de hitos

Mapear cada hito de las Secciones 6-7 del Plan de Proyecto a un nodo con todos sus atributos. Esto es el trabajo principal de este documento.

**Estructura de tabla sugerida para llenar:**

| ID | Nombre | Nivel | Rango edad | Dimensión | Depende de |
|---|---|---|---|---|---|
| H_N1_001 | [ ] | 1 | 0-6m | [ ] | — |
| H_N1_002 | [ ] | 1 | 0-6m | [ ] | H_N1_001 |
| ... | | | | | |

### 4. Script de seeding (Cypher)

Una vez definido el catálogo, crear el script Cypher que crea todos los nodos y aristas en ArcadeDB:

```cypher
// Estructura base del script (completar con los hitos reales)
CREATE (h:Hito {
  id_hito: 'H_N1_001',
  nombre: '[ ]',
  nivel: 1,
  ...
})

CREATE (h1:Hito {id_hito: 'H_N1_001'})
CREATE (h2:Hito {id_hito: 'H_N1_002'})
CREATE (h1)-[:PRECEDE_A]->(h2)
```

### 5. Integración con el motor de inferencia

Definir las consultas Cypher que usará `graph/navigator.py`:

```cypher
// Consulta 1: Obtener siguiente hito óptimo para un niño
// [ ] — definir la lógica de selección

// Consulta 2: Detectar hitos bloqueados
// [ ] — definir qué se considera "bloqueado"

// Consulta 3: Encontrar ruta alternativa
// [ ] — definir cómo el motor escoge la alternativa
```

---

## Preguntas abiertas

- [ ] ¿Cuántos hitos hay exactamente en las Secciones 6-7 del plan?
- [ ] ¿Las dimensiones (expresivo, comprensivo, fonológico) son las únicas categorías de hitos?
- [ ] ¿Un hito puede depender de múltiples hitos simultáneamente (AND) o es OR?
- [ ] ¿Cómo se representa en el grafo la condición de "Ticket de Rezago"?
- [ ] ¿El grafo varía por perfil de diagnóstico (afasia vs. disfasia) o es universal?
