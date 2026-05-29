# =============================================================
#  cargar_datos.py — Carga el CSV a Neo4j
#  Sistema de Recomendaciones de Videos
# =============================================================

import csv
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


def cargar_datos(ruta_csv: str):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    usuarios = {}   # id → propiedades
    videos   = {}
    tags     = {}
    relaciones = []

    # ── Leer CSV ──────────────────────────────────────────────
    with open(ruta_csv, newline="", encoding="utf-8-sig") as f:
        for fila in csv.DictReader(f, delimiter=',', quotechar='"'):
            oid  = fila["origen_id"]
            oti  = fila["origen_tipo"]
            did  = fila["destino_id"]
            dti  = fila["destino_tipo"]
            rel  = fila["relacion"]

            # Registrar nodo origen
            if oti == "Usuario" and oid not in usuarios:
                usuarios[oid] = {
                    "id":       oid,
                    "nombre":   fila["u_nombre"],
                    "edad":     int(fila["u_edad"]) if fila["u_edad"] else None,
                    "franja":   fila["u_franja"],
                    "registro": fila["u_registro"],
                }
            if oti == "Video" and oid not in videos:
                videos[oid] = {
                    "id":       oid,
                    "titulo":   fila["v_titulo"],
                    "duracion": int(fila["v_duracion_seg"]) if fila["v_duracion_seg"] else None,
                    "autor":    fila["v_autor"],
                    "pub":      fila["v_pub"],
                    "vistas":   int(fila["v_vistas"]) if fila["v_vistas"] else None,
                }

            # Registrar nodo destino
            if dti == "Video" and did not in videos:
                videos[did] = {
                    "id":       did,
                    "titulo":   fila["v_titulo"],
                    "duracion": int(fila["v_duracion_seg"]) if fila["v_duracion_seg"] else None,
                    "autor":    fila["v_autor"],
                    "pub":      fila["v_pub"],
                    "vistas":   int(fila["v_vistas"]) if fila["v_vistas"] else None,
                }
            if dti == "Tag" and did not in tags:
                tags[did] = {
                    "id":       did,
                    "nombre":   fila["t_nombre"],
                    "categoria":fila["t_cat"],
                }

            relaciones.append(fila)