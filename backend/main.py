from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv # 1. Nueva importación
import google.generativeai as genai

# 2. Cargar las variables del archivo .env a la memoria
load_dotenv()

app = FastAPI()

# 3. Llamar a la clave de forma segura sin escribirla en el código
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 4. Instanciar el modelo (Corregido a la versión válida)
model = genai.GenerativeModel('gemini-1.5-flash')

class QueryRequest(BaseModel):
    pregunta: str




@app.post("/api/query")
def process_query(request: QueryRequest):
    pregunta = request.pregunta.lower()
    conn = sqlite3.connect('hospital.db')
    
    esquema_bd = """
    Base de datos SQLite con las siguientes tablas y sus columnas exactas:
    - Atencion(OidIngreso, FechaAtencion)
    - Ingresos(OidIngreso, ConsecutivoIngreso, IdPaciente, ClaseIngreso, ViaIngreso, TipoRiesgo, FechaIngreso, FechaHospitalizacion, OidTriageA, CodigoCama, NombreCama, NombreGrupoCama, NombreSubgrupoCama, CodigoDiagnostico, NombreDiagnostico)
    - MedicamentoInsumo(OidIngreso, CodigoServicio, NombreServicio, Cantidad, FechaPrestacion, AreaServicio, Especialidad, OidMI)
    - Paciente(TipoDocumento, IdPaciente, NombrePaciente, FechaNacimiento, Sexo, Asegurador, Regimen, Departamento, Municipio, Zona)
    - ProgramacionCirugia(ConsecutivoProgramacion, IdPaciente, OidIngreso, CodigoServicio)
    - Servicios(OidIngreso, CodigoServicio, NombreServicio, Cantidad, FechaPrestacion, CodigoAreaServicio, AreaServicio, Especialidad, OidS)
    - Triage(OidTriage, FechaTriage, MotivoConsulta, TensionArterial, FrecuenciaCardiaca, FrecuenciaRespiratoria, Temperatura, IdPaciente2, CodigoTriage, ClasificacionTriage)
    """
    
    instrucciones = f"""
    Eres un analista de datos de un hospital experto en SQLite. 
    Devuelve EXCLUSIVAMENTE una consulta SQL válida que responda a la pregunta del usuario.
    No incluyas explicaciones ni formato markdown (```sql). SOLO el texto de la consulta.
    
    Esquema: {esquema_bd}
    
    Reglas CRÍTICAS:
    - Para ocupación o estado de camas, cuenta 'CodigoCama' en la tabla 'Ingresos'.
    - Busca en 'NombreSubgrupoCama' usando LIKE.
    
    Pregunta del usuario: {pregunta}
    """

    try:
        # 1. Intentamos consultar a Gemini
        respuesta_ia = model.generate_content(instrucciones)
        sql_generado = respuesta_ia.text.replace("```sql", "").replace("```", "").strip()
        
        if any(keyword in sql_generado.upper() for keyword in ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]):
            raise Exception("Operación destructiva SQL bloqueada.")
            
        origen_respuesta = "Generado dinámicamente por Gemini IA"

    except Exception as e:
        # 2. SISTEMA DE CONTINGENCIA (Si da error 429, no rompemos la app, usamos consultas seguras)
        print(f"⚠️ Alerta API: {e}. Activando contingencia automática.")
        origen_respuesta = "Generado por Contingencia (Límite de API alcanzado)"
        
        # Basado en tus datos reales mostrados en la imagen
        if "urgencias" in pregunta:
            sql_generado = "SELECT NombreSubgrupoCama, COUNT(OidIngreso) as TotalPacientes FROM Ingresos WHERE NombreSubgrupoCama LIKE '%URGENCIAS%' GROUP BY NombreSubgrupoCama;"
        elif "pediatria" in pregunta or "pediatría" in pregunta:
            sql_generado = "SELECT NombreDiagnostico, COUNT(OidIngreso) as Total Casos FROM Ingresos WHERE NombreSubgrupoCama LIKE '%PEDIATRIA%' GROUP BY NombreDiagnostico ORDER BY Total DESC LIMIT 5;"
        else:
            # Por defecto mostramos la ocupación general de todos los subgrupos
            sql_generado = "SELECT NombreSubgrupoCama, COUNT(CodigoCama) as CamasOcupadas FROM Ingresos GROUP BY NombreSubgrupoCama;"

    # 3. Ejecutamos el SQL (Ya sea el de Gemini o el de contingencia)
    try:
        df_resultados = pd.read_sql_query(sql_generado, conn)
        resultados_datos = df_resultados.to_dict(orient="records")
        conn.close()
        
        return {
            "pregunta_recibida": request.pregunta,
            "sql_ejecutado": sql_generado,
            "resultados": resultados_datos,
            "recomendacion_agente": origen_respuesta,
            "grafico_sugerido": "table"
        }
    except Exception as e_sql:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error en BD: {str(e_sql)}")