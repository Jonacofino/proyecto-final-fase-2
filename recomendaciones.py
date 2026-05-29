# =============================================================
#  recomendaciones.py — Algoritmo híbrido de recomendaciones
#  Sistema de Recomendaciones de Videos
# =============================================================

from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


class SistemaRecomendaciones:

    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def cerrar(self):
        self.driver.close()

    # ----------------------------------------------------------
    #  RECOMENDAR — algoritmo híbrido principal
    #  Combina filtrado colaborativo (30%) + contenido (70%)
    # ----------------------------------------------------------
    def recomendar(self, user_id: str, limite: int = 5) -> list[dict]:
        with self.driver.session() as s:
            resultado = s.run("""
                // Paso 1: Videos que ya vio el usuario
                MATCH (yo:Usuario {id: $uid})
                OPTIONAL MATCH (yo)-[:WATCHED]->(visto:Video)
                WITH yo, COLLECT(visto.id) AS ya_vistos

                // Paso 2: Obtener TODOS los videos no vistos y calcular Score Contenido
                MATCH (candidato:Video)
                WHERE NOT candidato.id IN ya_vistos
                  AND NOT EXISTS { MATCH (yo)-[:NOT_INTERESTED]->(candidato) }

                // Verificamos si los tags del video coinciden con los del usuario
                OPTIONAL MATCH (candidato)-[tw:TAGGED_WITH]->(tag:Tag)
                OPTIONAL MATCH (yo)-[ii:INTERESTED_IN]->(tag)
                WITH yo, candidato, SUM(CASE WHEN ii IS NOT NULL THEN ii.score * tw.relevancia ELSE 0 END) AS score_contenido

                // CANDADO: Descartamos inmediatamente cualquier video que no cruce con sus gustos
                WHERE score_contenido > 0

                // Paso 3: Calcular Score Colaborativo (puntos extra si lo vieron usuarios similares)
                OPTIONAL MATCH (candidato)<-[w:WATCHED]-(otro:Usuario)
                WHERE otro.id <> $uid
                // Calculamos similitud basada en tags comunes (minimo 1 para DB pequeñas)
                OPTIONAL MATCH (otro)-[:INTERESTED_IN]->(t:Tag)<-[:INTERESTED_IN]-(yo)
                WITH candidato, score_contenido, otro, COUNT(t) AS tags_comunes
                OPTIONAL MATCH (otro)-[l:LIKED]->(candidato)
                WITH candidato, score_contenido,
                     SUM(CASE WHEN tags_comunes >= 1 THEN tags_comunes * (CASE WHEN l IS NOT NULL THEN 1.5 ELSE 1.0 END) ELSE 0 END) AS score_colab

                // Paso 4: Score Final Híbrido
                WITH candidato,
                     (0.3 * score_colab + 0.7 * score_contenido) AS score_final
                WHERE score_final > 0

                RETURN candidato.id       AS video_id,
                       candidato.titulo   AS titulo,
                       candidato.autor    AS autor,
                       candidato.duracion_seg AS duracion,
                       candidato.vistas   AS vistas,
                       ROUND(score_final, 3) AS score
                ORDER BY score DESC
                LIMIT $limite
            """, uid=user_id, limite=limite)

            return [dict(r) for r in resultado]
    # ----------------------------------------------------------
    #  AGREGAR nodos y relaciones
    # ----------------------------------------------------------
    def agregar_usuario(self, uid, nombre, edad, franja, registro):
        with self.driver.session() as s:
            s.run("""
                MERGE (u:Usuario {id: $uid})
                SET u.nombre=$nombre, u.edad=$edad,
                    u.franja=$franja, u.fecha_registro=$registro
            """, uid=uid, nombre=nombre, edad=edad, franja=franja, registro=registro)
        print(f"Usuario {nombre} ({uid}) agregado.")

    def agregar_video(self, vid, titulo, duracion, autor, pub, vistas):
        with self.driver.session() as s:
            s.run("""
                MERGE (v:Video {id: $vid})
                SET v.titulo=$titulo, v.duracion_seg=$duracion,
                    v.autor=$autor, v.fecha_publicacion=$pub,
                    v.vistas=$vistas
            """, vid=vid, titulo=titulo, duracion=duracion,
                 autor=autor, pub=pub, vistas=vistas)
        print(f"Video '{titulo}' ({vid}) agregado.")

    def agregar_tag(self, tid, nombre, categoria):
        with self.driver.session() as s:
            s.run("""
                MERGE (t:Tag {id: $tid})
                SET t.nombre=$nombre, t.categoria=$categoria
            """, tid=tid, nombre=nombre, categoria=categoria)
        print(f"Tag '{nombre}' ({tid}) agregado.")

    def registrar_vista(self, uid, vid, duracion_vista, timestamp, completo):
        with self.driver.session() as s:
            s.run("""
                MATCH (u:Usuario {id:$uid}), (v:Video {id:$vid})
                MERGE (u)-[r:WATCHED {timestamp:$ts}]->(v)
                SET r.duracion_vista_seg=$dur, r.completo=$completo
            """, uid=uid, vid=vid, ts=timestamp, dur=duracion_vista, completo=completo)
        print(f"Vista registrada: {uid} -> {vid}")

    def registrar_like(self, uid, vid, timestamp):
        with self.driver.session() as s:
            s.run("""
                MATCH (u:Usuario {id:$uid}), (v:Video {id:$vid})
                MERGE (u)-[r:LIKED]->(v)
                SET r.timestamp=$ts
            """, uid=uid, vid=vid, ts=timestamp)
        print(f"Like registrado: {uid} -> {vid}")

    def marcar_no_interesado(self, uid, vid, timestamp):
        with self.driver.session() as s:
            s.run("""
                MATCH (u:Usuario {id:$uid}), (v:Video {id:$vid})
                MERGE (u)-[r:NOT_INTERESTED]->(v)
                SET r.timestamp=$ts
            """, uid=uid, vid=vid, ts=timestamp)
        print(f"'No interesado' registrado: {uid} -> {vid}")

    # ----------------------------------------------------------
    #  ELIMINAR nodos
    # ----------------------------------------------------------
    def eliminar_usuario(self, uid):
        with self.driver.session() as s:
            s.run("MATCH (u:Usuario {id:$uid}) DETACH DELETE u", uid=uid)
        print(f"Usuario {uid} eliminado.")

    def eliminar_video(self, vid):
        with self.driver.session() as s:
            s.run("MATCH (v:Video {id:$vid}) DETACH DELETE v", vid=vid)
        print(f"Video {vid} eliminado.")

    # ----------------------------------------------------------
    #  CONSULTAS de informacion
    # ----------------------------------------------------------
    def listar_usuarios(self):
        with self.driver.session() as s:
            r = s.run("MATCH (u:Usuario) RETURN u.id AS id, u.nombre AS nombre, u.edad AS edad, u.franja AS franja ORDER BY u.id")
            return [dict(x) for x in r]

    def listar_videos(self):
        with self.driver.session() as s:
            r = s.run("MATCH (v:Video) RETURN v.id AS id, v.titulo AS titulo, v.autor AS autor, v.duracion_seg AS duracion ORDER BY v.id")
            return [dict(x) for x in r]

    def perfil_usuario(self, uid):
        with self.driver.session() as s:
            tags = s.run("""
                MATCH (u:Usuario {id:$uid})-[r:INTERESTED_IN]->(t:Tag)
                RETURN t.nombre AS tag, r.score AS score ORDER BY score DESC
            """, uid=uid)
            vistos = s.run("""
                MATCH (u:Usuario {id:$uid})-[:WATCHED]->(v:Video)
                RETURN v.titulo AS titulo, v.id AS id
            """, uid=uid)
            return {
                "tags": [dict(t) for t in tags],
                "vistos": [dict(v) for v in vistos]
            }
        