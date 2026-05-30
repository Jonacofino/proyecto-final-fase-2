# Sistema de Recomendaciones de Videos
**CC2003 – Algoritmos y Estructura de Datos | Universidad del Valle de Guatemala**

Integrantes: Jonathan Cofiño (251252) · José Matías (251170) · Dostyn López (251404)

---

## ¿Qué hace este sistema?

Recomienda videos a usuarios basándose en un **algoritmo híbrido** que combina:
- **Filtrado colaborativo (70%):** usuarios con gustos similares → sus videos no vistos son candidatos
- **Filtrado por contenido (30%):** tags del video coinciden con los intereses del usuario

El sistema está implementado en **Python** con **Neo4j** como base de datos de grafos.

---

## Requisitos de software

| Software | Versión mínima | Descarga |
|---|---|---|
| Python | 3.10+ | https://python.org |
| Neo4j Desktop | 2.x | https://neo4j.com/download |
| neo4j (driver Python) | 5.x | `pip install neo4j` |

---

## Instalación paso a paso

### 1. Instalar el driver de Neo4j para Python
```bash
pip install neo4j
```

### 2. Configurar Neo4j Desktop
1. Abre Neo4j Desktop
2. Crea un nuevo proyecto local
3. Inicia la base de datos (botón **Start**)
4. Anota tu contraseña

### 3. Configurar la conexión
Abre el archivo `config.py` y ajusta tus credenciales:
```python
NEO4J_URI      = "neo4j://127.0.0.1:7687"
NEO4J_USER     = "neo4j"
NEO4J_PASSWORD = "tu_contraseña_aqui"
```

### 4. Poner el CSV de datos en la misma carpeta
El archivo `base_de_datos_supuestamente_funcional.txt` debe estar junto a los archivos `.py`.

---

## Cómo ejecutar el sistema

```bash
python main.py
```

Se abre un menú interactivo con las siguientes opciones:

```
  1. Cargar base de datos desde CSV        ← hacer esto primero
  2. Ver recomendaciones para un usuario
  3. Agregar usuario
  4. Agregar video
  5. Registrar que un usuario vio un video
  6. Registrar like
  7. Marcar video como "No me interesa"
  8. Eliminar usuario
  9. Eliminar video
 10. Listar todos los usuarios
 11. Listar todos los videos
 12. Ver perfil de un usuario
  0. Salir
```

---

## Flujo de uso típico

```
1. Ejecutar: python main.py
2. Opción 1 → cargar el CSV (solo la primera vez)
3. Opción 10 → ver qué usuarios existen (U01, U02, ...)
4. Opción 2 → escribir un ID de usuario → ver sus recomendaciones
```

---

## Estructura de archivos

```
proyecto_recomendacion/
├── main.py                                  # Menú principal
├── recomendaciones.py                       # Algoritmo + operaciones CRUD
├── cargar_datos.py                          # Carga el CSV a Neo4j
├── config.py                                # Credenciales de conexión
├── base_de_datos_supuestamente_funcional.txt  # Base de datos
└── README.md                                # Este archivo
```

---

## Estructura de la base de datos (grafos)

### Nodos
| Nodo | Propiedades |
|---|---|
| Usuario | id, nombre, edad, franja, fecha_registro |
| Video | id, titulo, duracion_seg, autor, fecha_publicacion, vistas |
| Tag | id, nombre, categoria |

### Relaciones
| Relación | Dirección | Propiedades |
|---|---|---|
| WATCHED | Usuario → Video | duracion_vista_seg, timestamp, completo |
| LIKED | Usuario → Video | timestamp |
| SHARED | Usuario → Video | timestamp, plataforma |
| NOT_INTERESTED | Usuario → Video | timestamp |
| TAGGED_WITH | Video → Tag | relevancia |
| INTERESTED_IN | Usuario → Tag | score, ultima_actualizacion |

---

## Algoritmo de recomendaciones

```
Score final = 0.6 × score_colaborativo + 0.4 × score_contenido

score_colaborativo:
  - Buscar usuarios con tags de interés en común
  - Sus videos no vistos por el usuario activo son candidatos
  - Peso extra si el usuario similar dio like (+50%)

score_contenido:
  - Tags del video candidato × score de interés del usuario en ese tag
  - Multiplicado por la relevancia del tag en el video

Filtros de exclusión:
  - Videos ya vistos por el usuario
  - Videos marcados como NOT_INTERESTED
```
