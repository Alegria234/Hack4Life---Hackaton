from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from DatabaseManager import DatabaseManager
from AIService import AIService

# Carga las variables del archivo .env (incluyendo GEMINI_API_KEY)
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

db_manager = DatabaseManager()
ai_service = AIService()

class QueryRequest(BaseModel):
    pregunta: str

# --- ENDPOINTS ---

@app.on_event("startup")
def startup_db():
    db_manager.init_db()

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