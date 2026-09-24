from passlib.context import CryptContext
from pydantic import BaseModel
import sqlite3
from fastapi import FastAPI, HTTPException

from DatabaseManager import DatabaseManager

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI()

class LoginData(BaseModel):
    username: str
    password: str

def obtener_hash_password(password: str) -> str:
    return pwd_context.hash(password)

def inicializar_tabla_usuarios(db_path: str):
    """Crea la tabla de usuarios y siembra usuarios por defecto si no existen."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM Usuarios")
    if cursor.fetchone()[0] == 0:
        pass_medico = obtener_hash_password("1234")
        pass_admin = obtener_hash_password("1234")
        cursor.executemany("""
            INSERT INTO Usuarios (username, password_hash, rol) VALUES (?, ?, ?)
        """, [
            ("medico", pass_medico, "MEDICO"),
            ("admin", pass_admin, "DIRECTIVO")
        ])
        conn.commit()
    conn.close()

@app.post("/api/login")
def login(datos: LoginData):
    db_path = DatabaseManager()._get_path()
    
    inicializar_tabla_usuarios(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash, rol FROM Usuarios WHERE username = ?", (datos.username,))
    usuario = cursor.fetchone()
    conn.close()

    if not usuario or not pwd_context.verify(datos.password, usuario[2]):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    return {
        "mensaje": "Login exitoso",
        "usuario": {
            "id": usuario[0],
            "username": usuario[1],
            "rol": usuario[3]  # 'MEDICO' o 'DIRECTIVO'
        },
        "redirect": "/chat" if usuario[3] == "MEDICO" else "/dashboard"
    }