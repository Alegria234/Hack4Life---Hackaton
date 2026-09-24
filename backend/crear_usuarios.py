import sqlite3
from passlib.context import CryptContext

# Configuración de encriptación (la misma de tu main.py)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def crear_usuarios_prueba():
    # Nos conectamos a la base de datos
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()

    # 1. Crear la tabla por si no existe
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        rol TEXT NOT NULL
    )
    ''')

    # 2. Datos de los usuarios que vamos a crear
    usuarios = [
        {"username": "admin", "password": "123", "rol": "admin"},
        {"username": "medico", "password": "123", "rol": "user"}
    ]

    # 3. Insertar los usuarios encriptando la contraseña
    for u in usuarios:
        hash_generado = pwd_context.hash(u["password"])
        try:
            cursor.execute(
                "INSERT INTO Usuarios (username, password_hash, rol) VALUES (?, ?, ?)",
                (u["username"], hash_generado, u["rol"])
            )
            print(f"✅ Usuario '{u['username']}' creado exitosamente.")
        except sqlite3.IntegrityError:
            print(f"⚠️ El usuario '{u['username']}' ya existe en la base de datos.")

    # Guardar cambios y cerrar
    conn.commit()
    conn.close()
    print("Proceso terminado.")

if __name__ == "__main__":
    crear_usuarios_prueba()