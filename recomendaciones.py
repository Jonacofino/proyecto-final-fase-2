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
