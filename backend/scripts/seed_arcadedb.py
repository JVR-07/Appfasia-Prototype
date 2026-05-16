import os
from neo4j import GraphDatabase

# Hitos del Nivel 1 y 2
HITOS_SEED = [
    # Nivel 1 (0-2 años)
    {"id": "H_N1_001", "descripcion": "Imitación vocal simple", "nivel": 1, "bloqueante": True},
    {"id": "H_N1_002", "descripcion": "Uso de jerga expresiva", "nivel": 1, "bloqueante": False},
    {"id": "H_N1_003", "descripcion": "Balbuceo silábico", "nivel": 1, "bloqueante": True},
    {"id": "H_N1_004", "descripcion": "Señalar objetos para pedir", "nivel": 1, "bloqueante": False},
    {"id": "H_N1_005", "descripcion": "Uso de 5 a 10 palabras con sentido", "nivel": 1, "bloqueante": True},
    
    # Nivel 2 (2-4 años)
    {"id": "H_N2_001", "descripcion": "Combinación de 2 palabras (ej. Mamá agua)", "nivel": 2, "bloqueante": True},
    {"id": "H_N2_002", "descripcion": "Uso de pronombres yo/tú", "nivel": 2, "bloqueante": False},
    {"id": "H_N2_003", "descripcion": "Vocabulario expresivo de 50 palabras", "nivel": 2, "bloqueante": True},
    {"id": "H_N2_004", "descripcion": "Responde preguntas de Sí/No", "nivel": 2, "bloqueante": False},
    {"id": "H_N2_005", "descripcion": "Uso de oraciones simples de 3 elementos", "nivel": 2, "bloqueante": True},
]

# Relaciones: Origen -> Destino (Prerrequisitos)
RELACIONES_SEED = [
    ("H_N1_001", "H_N1_003"),
    ("H_N1_003", "H_N1_005"),
    ("H_N1_004", "H_N2_001"),
    ("H_N1_005", "H_N2_001"),
    ("H_N2_001", "H_N2_003"),
    ("H_N2_003", "H_N2_005"),
    ("H_N1_002", "H_N2_002"),
    ("H_N2_002", "H_N2_005"),
]

import httpx
import asyncio

def execute_cypher(client: httpx.Client, query: str):
    response = client.post(
        "/api/v1/command/appfasia_graph",
        json={"language": "cypher", "command": query}
    )
    if response.status_code not in (200, 201):
        print(f"[!] Error ejecutando query: {response.text}")
    return response

def seed_arcadedb():
    url = "http://arcadedb:2480"
    user = os.getenv("ARCADEDB_USER", "root")
    password = os.getenv("ARCADEDB_ROOT_PASSWORD", "-Admin07-")

    print(f"[*] Conectando a ArcadeDB HTTP en {url}")
    
    # Aseguramos que la base de datos existe
    with httpx.Client(base_url=url, auth=(user, password), timeout=30.0) as client:
        res = client.post("/api/v1/server", json={"command": "create database appfasia_graph"})
        if res.status_code == 200:
            print("[*] Base de datos creada o ya existía.")
            
        print("[*] Limpiando grafo existente...")
        execute_cypher(client, "MATCH (n) DETACH DELETE n")

        print("[*] Insertando hitos (nodos)...")
        for hito in HITOS_SEED:
            query = f"""
            CREATE (h:Hito {{
                id: '{hito["id"]}',
                descripcion: '{hito["descripcion"]}',
                nivel: {hito["nivel"]},
                es_bloqueante: {'true' if hito["bloqueante"] else 'false'}
            }})
            """
            execute_cypher(client, query)
        
        print("[*] Creando relaciones PREREQUISITO_DE (aristas)...")
        for origen, destino in RELACIONES_SEED:
            query = f"""
            MATCH (o:Hito {{id: '{origen}'}}), (d:Hito {{id: '{destino}'}})
            CREATE (o)-[:PREREQUISITO_DE {{peso: 1.0}}]->(d)
            """
            execute_cypher(client, query)

    print(f"[+] Seeding de ArcadeDB completado. {len(HITOS_SEED)} nodos y {len(RELACIONES_SEED)} relaciones insertadas.")

if __name__ == "__main__":
    seed_arcadedb()
