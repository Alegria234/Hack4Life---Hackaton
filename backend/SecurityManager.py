import re
import sqlite3
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
from passlib.context import CryptContext  # type: ignore
from pydantic import BaseModel  # type: ignore
from fastapi import HTTPException  # type: ignore

class LoginData(BaseModel):
    username: str
    password: str

class SecurityManager:

    FORBIDDEN_KEYWORDS = [
        r"\bDROP\b", r"\bDELETE\b", r"\bUPDATE\b", r"\bINSERT\b", 
        r"\bALTER\b", r"\bTRUNCATE\b", r"\bCREATE\b", r"\bEXEC\b"
    ]

    PII_COLUMNS = ['nombrepaciente', 'idpaciente', 'idpaciente2', 'tipodocumento']

    def __init__(self, db_path: str = "data/hospital.db"):
        self.db_path = db_path
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def obtener_hash_password(self, password: str) -> str:
        """Genera el hash Bcrypt de una contraseña en texto plano."""
        return self.pwd_context.hash(password)

    def verificar_password(self, plain_password: str, hashed_password: str) -> bool:
        """Compara una contraseña en texto plano contra su hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def init_usuarios_db(self):
        """Crea la tabla Usuarios si no existe y siembra credenciales de prueba."""
        conn = sqlite3.connect(self.db_path)
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
            usuarios_iniciales = [
                ("medico", self.obtener_hash_password("1234"), "medico"),
                ("admin", self.obtener_hash_password("1234"), "admin")
            ]
            cursor.executemany("""
                INSERT INTO Usuarios (username, password_hash, rol) VALUES (?, ?, ?)
            """, usuarios_iniciales)
            conn.commit()
            
        conn.close()

    def autenticar_usuario(self, username: str, password: str) -> dict:
        """Verifica credenciales y retorna los datos del usuario o lanza HTTPException."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, username, password_hash, rol FROM Usuarios WHERE username = ?", 
            (username,)
        )
        usuario = cursor.fetchone()
        conn.close()

        if not usuario or not self.verificar_password(password, usuario[2]):
            raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

        return {
            "id": usuario[0],
            "username": usuario[1],
            "rol": usuario[3]  # 'admin' o 'medico'
        }

    @classmethod
    def validar_sql_seguro(cls, sql_query: str) -> str:
        query_limpia = re.sub(r'```sql|```', '', sql_query, flags=re.IGNORECASE).strip()
        query_upper = query_limpia.upper()

        if not query_upper.startswith("SELECT"):
            raise ValueError("Solo se permiten consultas de lectura de tipo (SELECT).")

        if ";" in query_upper[:-1]:  
            raise ValueError("No se permiten múltiples sentencias SQL concatenadas.")

        for keyword in cls.FORBIDDEN_KEYWORDS:
            if re.search(keyword, query_upper):
                raise ValueError(f"Operación destructiva prohibida detectada '{keyword}'.")

        return query_limpia

    @classmethod
    def anonimizar_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        cols_a_modificar = [
            col for col in df.columns 
            if str(col).lower().replace("_", "").replace(" ", "") in cls.PII_COLUMNS
        ]
        
        if not cols_a_modificar:
            return df

        df_anonimo = df.copy()

        for col in cols_a_modificar:
            col_lower = str(col).lower().replace("_", "").replace(" ", "")

            if 'nombre' in col_lower:
                df_anonimo[col] = "PACIENTE_ANÓNIMO"
                
            elif 'id' in col_lower or 'documento' in col_lower:
                s_str = df_anonimo[col].astype(str).str.split('.').str[0].str.strip()
                
                ultimos_dos = s_str.str[-2:]
                df_anonimo[col] = np.where(
                    (s_str == "") | (s_str == "nan") | (s_str == "None"),
                    "",
                    "***" + ultimos_dos
                )

        return df_anonimo