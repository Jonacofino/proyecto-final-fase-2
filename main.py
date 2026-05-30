# =============================================================
#  main.py — Menú principal del Sistema de Recomendaciones
#  Sistema de Recomendaciones de Videos
# =============================================================

from recomendaciones import SistemaRecomendaciones
from cargar_datos import cargar_datos
from datetime import datetime


def imprimir_separador():
    print("\n" + "═" * 55)

def imprimir_titulo():
    print("""
╔═══════════════════════════════════════════════════════╗
║       SISTEMA DE RECOMENDACIONES DE VIDEOS            ║
║       CC2003 – Algoritmos y Estructura de Datos       ║
╚═══════════════════════════════════════════════════════╝""")

def menu_principal():
    imprimir_titulo()
    print("""
  1. Cargar base de datos desde CSV
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
""")
    return input("  Elige una opción: ").strip()


def main():
    sistema = SistemaRecomendaciones()

    while True:
        imprimir_separador()
        opcion = menu_principal()

        # ── 1. Cargar CSV ──────────────────────────────────────
        if opcion == "1":
            ruta = input("  Ruta del archivo CSV [base_de_datos_supuestamente_funcional.txt]: ").strip()
            if not ruta:
                ruta = "base_de_datos_supuestamente_funcional.txt"
            print()
            cargar_datos(ruta)

        # ── 2. Recomendaciones ─────────────────────────────────
        elif opcion == "2":
            uid = input("  ID del usuario (ej. U01): ").strip().upper()
            n   = input("  ¿Cuántas recomendaciones? [5]: ").strip()
            n   = int(n) if n.isdigit() else 5

            recomendaciones = sistema.recomendar(uid, n)

            if not recomendaciones:
                print(f"\n  ⚠️  No se encontraron recomendaciones para {uid}.")
                print("     Asegúrate de que el usuario tiene tags de interés registrados.")
            else:
                print(f"\n  🎬  Recomendaciones para {uid}:\n")
                for i, r in enumerate(recomendaciones, 1):
                    print(f"  {i}. {r['titulo']}")
                    print(f"     Autor: {r['autor']}  |  Duración: {r['duracion']}s  |  Vistas: {r['vistas']:,}")
                    print(f"     Score: {r['score']}\n")

        # ── 3. Agregar usuario ─────────────────────────────────
        elif opcion == "3":
            uid     = input("  ID (ej. U21): ").strip().upper()
            nombre  = input("  Nombre: ").strip()
            edad    = input("  Edad: ").strip()
            franja  = input("  Franja horaria (mañana/tarde/noche): ").strip()
            registro = datetime.now().strftime("%Y-%m-%d")
            sistema.agregar_usuario(uid, nombre, int(edad), franja, registro)

        # ── 4. Agregar video ───────────────────────────────────
        elif opcion == "4":
            vid     = input("  ID (ej. V31): ").strip().upper()
            titulo  = input("  Título: ").strip()
            duracion= input("  Duración en segundos: ").strip()
            autor   = input("  Autor (ej. @nombre): ").strip()
            pub     = datetime.now().strftime("%Y-%m-%d")
            vistas  = input("  Vistas: ").strip()
            sistema.agregar_video(vid, titulo, int(duracion), autor, pub, int(vistas))

        # ── 5. Registrar vista ─────────────────────────────────
        elif opcion == "5":
            uid      = input("  ID usuario: ").strip().upper()
            vid      = input("  ID video: ").strip().upper()
            dur      = input("  Segundos que vio: ").strip()
            completo = input("  ¿Lo vio completo? (s/n): ").strip().lower() == "s"
            ts       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sistema.registrar_vista(uid, vid, int(dur), ts, completo)

        # ── 6. Like ────────────────────────────────────────────
        elif opcion == "6":
            uid = input("  ID usuario: ").strip().upper()
            vid = input("  ID video: ").strip().upper()
            ts  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sistema.registrar_like(uid, vid, ts)

        # ── 7. No me interesa ──────────────────────────────────
        elif opcion == "7":
            uid = input("  ID usuario: ").strip().upper()
            vid = input("  ID video: ").strip().upper()
            ts  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sistema.marcar_no_interesado(uid, vid, ts)

        # ── 8. Eliminar usuario ────────────────────────────────
        elif opcion == "8":
            uid = input("  ID usuario a eliminar: ").strip().upper()
            confirmar = input(f"  ¿Seguro que quieres eliminar {uid}? (s/n): ").strip().lower()
            if confirmar == "s":
                sistema.eliminar_usuario(uid)

        # ── 9. Eliminar video ──────────────────────────────────
        elif opcion == "9":
            vid = input("  ID video a eliminar: ").strip().upper()
            confirmar = input(f"  ¿Seguro que quieres eliminar {vid}? (s/n): ").strip().lower()
            if confirmar == "s":
                sistema.eliminar_video(vid)

        # ── 10. Listar usuarios ────────────────────────────────
        elif opcion == "10":
            usuarios = sistema.listar_usuarios()
            print(f"\n  👥 {len(usuarios)} usuarios registrados:\n")
            for u in usuarios:
                print(f"  {u['id']} | {u['nombre']:<15} | Edad: {u['edad']} | Franja: {u['franja']}")

        # ── 11. Listar videos ──────────────────────────────────
        elif opcion == "11":
            videos = sistema.listar_videos()
            print(f"\n  🎬 {len(videos)} videos registrados:\n")
            for v in videos:
                print(f"  {v['id']} | {v['titulo']:<35} | {v['autor']:<15} | {v['duracion']}s")

        # ── 12. Perfil usuario ─────────────────────────────────
        elif opcion == "12":
            uid  = input("  ID usuario: ").strip().upper()
            data = sistema.perfil_usuario(uid)
            print(f"\n  🏷️  Tags de interés de {uid}:")
            for t in data["tags"]:
                barra = "█" * int(t["score"] * 10)
                print(f"    {t['tag']:<15} {barra} ({t['score']})")
            print(f"\n  📺 Videos vistos ({len(data['vistos'])}):")
            for v in data["vistos"]:
                print(f"    {v['id']} — {v['titulo']}")

        # ── 0. Salir ───────────────────────────────────────────
        elif opcion == "0":
            sistema.cerrar()
            print("\n  ¡Hasta luego! 👋\n")
            break

        else:
            print("  ⚠️  Opción no válida, intenta de nuevo.")


if __name__ == "__main__":
    main()
