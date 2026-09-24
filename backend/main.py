from fastapi import FastAPI, HTTPException  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from pydantic import BaseModel  # type: ignore
from dotenv import load_dotenv  # type: ignore

from DatabaseManager import DatabaseManager
from AIService import AIService
from SecurityManager import SecurityManager, LoginData

load_dotenv()

app = FastAPI(
    title="API Gestión Hospitalaria - Hack4Life 2026",
    description="Backend para analítica hospitalaria y Agente IA NL2SQL"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancias de Servicios
db_manager = DatabaseManager()
ai_service = AIService()
security_manager = SecurityManager(db_path=ai_service.db_path)

class QueryRequest(BaseModel):
    pregunta: str

# --- EVENTOS ---

@app.on_event("startup")
def startup_db():
    db_manager.init_db()
    security_manager.init_usuarios_db()

# --- ENDPOINTS ---

@app.post("/api/login")
def login(datos: LoginData):
    usuario_autenticado = security_manager.autenticar_usuario(datos.username, datos.password)
    return {
        "mensaje": "Login exitoso",
        "usuario": usuario_autenticado,
        "redirect": "/chat" if usuario_autenticado["rol"].lower() == "medico" else "/dashboard"
    }

@app.post("/api/query")
def process_query(request: QueryRequest):
    try:
        return ai_service.ejecutar_consulta_conversacional(request.pregunta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando la consulta: {str(e)}")

@app.post("/api/admin/poblar-datos")
def poblar_datos():
    try:
        db_manager.cargar_excel_a_sqlite()
        return {"status": "success", "message": "Proceso de ingesta finalizado."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alertas")
def get_alertas():
    return ai_service.obtener_alertas_sistema()