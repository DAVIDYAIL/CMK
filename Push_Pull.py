import os
import subprocess

def git_push():
    try:
        # Paso 0: git pull para traer cambios remotos
        subprocess.run(["git", "pull"], check=True)
        print("🔄 Cambios remotos sincronizados (git pull).")

        # Pedir mensaje de commit
        commit_msg = input("✏️ Escribe el mensaje del commit: ").strip()
        if not commit_msg:
            print("❌ No se puede hacer commit sin mensaje.")
            return

        # Paso 1: git add .
        subprocess.run(["git", "add", "."], check=True)
        print("✅ Archivos agregados.")

        # Paso 2: git commit -m "mensaje"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        print("✅ Commit creado.")

        # Paso 3: git push
        subprocess.run(["git", "push"], check=True)
        print("✅ Cambios enviados a GitHub.")

    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error durante ejecución de Git: {e}")

if __name__ == "__main__":
    git_push()
