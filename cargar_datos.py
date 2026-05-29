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

    # ── Escribir en Neo4j ─────────────────────────────────────
    with driver.session() as s:
        # Limpiar base de datos antes de cargar
        s.run("MATCH (n) DETACH DELETE n")
        print("Base de datos limpia.")

        # Nodos Usuario
        for u in usuarios.values():
            s.run("""
                MERGE (u:Usuario {id: $id})
                SET u.nombre=$nombre, u.edad=$edad,
                    u.franja=$franja, u.fecha_registro=$registro
            """, **u)
        print(f"  {len(usuarios)} usuarios creados.")

        # Nodos Video
        for v in videos.values():
            s.run("""
                MERGE (v:Video {id: $id})
                SET v.titulo=$titulo, v.duracion_seg=$duracion,
                    v.autor=$autor, v.fecha_publicacion=$pub,
                    v.vistas=$vistas
            """, **v)
        print(f"  {len(videos)} videos creados.")

        # Nodos Tag
        for t in tags.values():
            s.run("""
                MERGE (t:Tag {id: $id})
                SET t.nombre=$nombre, t.categoria=$categoria
            """, **t)
        print(f"  {len(tags)} tags creados.")

        # Relaciones
        for fila in relaciones:
            rel = fila["relacion"]

            if rel == "WATCHED":
                s.run("""
                    MATCH (u:Usuario {id:$uid}), (v:Video {id:$vid})
                    MERGE (u)-[r:WATCHED {timestamp:$ts}]->(v)
                    SET r.duracion_vista_seg = $dur,
                        r.completo = ($completo = 'true')
                """, uid=fila["origen_id"], vid=fila["destino_id"],
                     ts=fila["r_timestamp"], dur=int(fila["r_duracion_seg"]) if fila["r_duracion_seg"] else 0,
                     completo=fila["r_completo"])

            elif rel == "LIKED":
                s.run("""
                    MATCH (u:Usuario {id:$uid}), (v:Video {id:$vid})
                    MERGE (u)-[r:LIKED]->(v)
                    SET r.timestamp=$ts
                """, uid=fila["origen_id"], vid=fila["destino_id"], ts=fila["r_timestamp"])

            elif rel == "SHARED":
                s.run("""
                    MATCH (u:Usuario {id:$uid}), (v:Video {id:$vid})
                    MERGE (u)-[r:SHARED]->(v)
                    SET r.timestamp=$ts, r.plataforma=$plat
                """, uid=fila["origen_id"], vid=fila["destino_id"],
                     ts=fila["r_timestamp"], plat=fila["r_plataforma"])

            elif rel == "NOT_INTERESTED":
                s.run("""
                    MATCH (u:Usuario {id:$uid}), (v:Video {id:$vid})
                    MERGE (u)-[r:NOT_INTERESTED]->(v)
                    SET r.timestamp=$ts
                """, uid=fila["origen_id"], vid=fila["destino_id"], ts=fila["r_timestamp"])

            elif rel == "TAGGED_WITH":
                s.run("""
                    MATCH (v:Video {id:$vid}), (t:Tag {id:$tid})
                    MERGE (v)-[r:TAGGED_WITH]->(t)
                    SET r.relevancia = toFloat($rel)
                """, vid=fila["origen_id"], tid=fila["destino_id"],
                     rel=fila["r_relevancia"] if fila["r_relevancia"] else "0.5")

            elif rel == "INTERESTED_IN":
                s.run("""
                    MATCH (u:Usuario {id:$uid}), (t:Tag {id:$tid})
                    MERGE (u)-[r:INTERESTED_IN]->(t)
                    SET r.score = toFloat($score),
                        r.ultima_actualizacion = $ts
                """, uid=fila["origen_id"], tid=fila["destino_id"],
                     score=fila["r_score"] if fila["r_score"] else "0.5",
                     ts=fila["r_timestamp"])

        print(f"  {len(relaciones)} relaciones creadas.")

    driver.close()
    print("\n✅ Base de datos cargada exitosamente.")


if __name__ == "__main__":
    import sys
    ruta = sys.argv[1] if len(sys.argv) > 1 else "base_de_datos_supuestamente_funcional.txt"
    cargar_datos(ruta)
