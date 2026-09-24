# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import sqlite3
# import pandas as pd
# import os
# import google.generativeai as genai

# app = FastAPI()

# # 1. Habilitar CORS para que React (Frontend) pueda comunicarse sin bloqueos
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Configuración de Gemini
# # Te recomiendo usar variables de entorno, pero para la rapidez del hackatón 
# # puedes pegar tu clave directamente aquí (borra esto antes de subirlo a un repo público)
# os.environ["GEMINI_API_KEY"] ="AQ.Ab8RN6JbDST0G8kL_pq-fj3vZXxANspnbqYN7ChJ5lP-2XEBHw"
# genai.configure(api_key=os.environ["GEMINI_API_KEY"])
# # Instanciar el modelo (usamos flash porque es el más rápido para este reto)
# # Instanciar el modelo (LA CORRECCIÓN)
# model = genai.GenerativeModel('gemini-3.6-flash')
# class QueryRequest(BaseModel):
#     pregunta: str


# from passlib.context import CryptContext
# from pydantic import BaseModel

# # Configuración de encriptación Bcrypt
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# class LoginData(BaseModel):
#     username: str
#     password: str

# # Función utilitaria para cuando quieras insertar un usuario de prueba en la base de datos
# def obtener_hash_password(password):
#     return pwd_context.hash(password)


# @app.get("/api/dashboard")
# def obtener_dashboard():
#     try:
#         conn = sqlite3.connect('hospital.db')
#         conn.row_factory = sqlite3.Row
#         cursor = conn.cursor()

#         # 1. Datos para el Gráfico de Triage
#         cursor.execute("SELECT clasificacion_triage as nombre, COUNT(*) as valor FROM Triage GROUP BY clasificacion_triage")
#         triage_data = [dict(row) for row in cursor.fetchall()]

#         # 2. Datos para la Tabla de Últimos Ingresos
#         cursor.execute("SELECT id, tipo_servicio, fecha_ingreso FROM Ingresos ORDER BY id DESC LIMIT 4")
#         ingresos_data = [dict(row) for row in cursor.fetchall()]

#         conn.close()
#         return {
#             "triage": triage_data,
#             "ingresos": ingresos_data
#         }
#     except Exception as e:
#         return {"error": str(e)}

# @app.post("/api/login")
# def login(datos: LoginData):
#     conn = sqlite3.connect('hospital.db')
#     cursor = conn.cursor()
#     # Buscamos al usuario por su username
#     cursor.execute("SELECT id, username, password_hash, rol FROM Usuarios WHERE username = ?", (datos.username,))
#     usuario = cursor.fetchone()
#     conn.close()

#     # Validamos si existe y si la contraseña coincide con el Hash encriptado
#     if not usuario or not pwd_context.verify(datos.password, usuario[2]):
#         raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

#     # Si es exitoso, devolvemos los datos (sin el hash)
#     return {
#         "mensaje": "Login exitoso",
#         "usuario": {
#             "id": usuario[0],
#             "username": usuario[1],
#             "rol": usuario[3] # 'admin' o 'user'
#         }
#     }

# @app.post("/api/query")
# def process_query(request: QueryRequest):
#     pregunta = request.pregunta.lower()
#     conn = sqlite3.connect('hospital.db')
    
#     esquema_bd = """
#     Base de datos SQLite con las siguientes tablas y sus columnas exactas:
#     - Atencion(OidIngreso, FechaAtencion)
#     - Ingresos(OidIngreso, ConsecutivoIngreso, IdPaciente, ClaseIngreso, ViaIngreso, TipoRiesgo, FechaIngreso, FechaHospitalizacion, OidTriageA, CodigoCama, NombreCama, NombreGrupoCama, NombreSubgrupoCama, CodigoDiagnostico, NombreDiagnostico)
#     - MedicamentoInsumo(OidIngreso, CodigoServicio, NombreServicio, Cantidad, FechaPrestacion, AreaServicio, Especialidad, OidMI)
#     - Paciente(TipoDocumento, IdPaciente, NombrePaciente, FechaNacimiento, Sexo, Asegurador, Regimen, Departamento, Municipio, Zona)
#     - ProgramacionCirugia(ConsecutivoProgramacion, IdPaciente, OidIngreso, CodigoServicio)
#     - Servicios(OidIngreso, CodigoServicio, NombreServicio, Cantidad, FechaPrestacion, CodigoAreaServicio, AreaServicio, Especialidad, OidS)
#     - Triage(OidTriage, FechaTriage, MotivoConsulta, TensionArterial, FrecuenciaCardiaca, FrecuenciaRespiratoria, Temperatura, IdPaciente2, CodigoTriage, ClasificacionTriage)
#     """
    
#     instrucciones = f"""
#     Eres un analista de datos de un hospital experto en SQLite. 
#     Devuelve EXCLUSIVAMENTE una consulta SQL válida que responda a la pregunta del usuario.
#     No incluyas explicaciones ni formato markdown (```sql). SOLO el texto de la consulta.
    
#     Esquema: {esquema_bd}
    
#     Reglas CRÍTICAS:
#     - Para ocupación o estado de camas, cuenta 'CodigoCama' en la tabla 'Ingresos'.
#     - Busca en 'NombreSubgrupoCama' usando LIKE.
    
#     Pregunta del usuario: {pregunta}
#     """

#     try:
#         # 1. Intentamos consultar a Gemini
#         respuesta_ia = model.generate_content(instrucciones)
#         sql_generado = respuesta_ia.text.replace("```sql", "").replace("```", "").strip()
        
#         if any(keyword in sql_generado.upper() for keyword in ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]):
#             raise Exception("Operación destructiva SQL bloqueada.")
            
#         origen_respuesta = "Generado dinámicamente por Gemini IA"

#     except Exception as e:
#         # 2. SISTEMA DE CONTINGENCIA (Si da error 429, no rompemos la app, usamos consultas seguras)
#         print(f"⚠️ Alerta API: {e}. Activando contingencia automática.")
#         origen_respuesta = "Generado por Contingencia (Límite de API alcanzado)"
        
#         # Basado en tus datos reales mostrados en la imagen
#         if "urgencias" in pregunta:
#             sql_generado = "SELECT NombreSubgrupoCama, COUNT(OidIngreso) as TotalPacientes FROM Ingresos WHERE NombreSubgrupoCama LIKE '%URGENCIAS%' GROUP BY NombreSubgrupoCama;"
#         elif "pediatria" in pregunta or "pediatría" in pregunta:
#             sql_generado = "SELECT NombreDiagnostico, COUNT(OidIngreso) as Total Casos FROM Ingresos WHERE NombreSubgrupoCama LIKE '%PEDIATRIA%' GROUP BY NombreDiagnostico ORDER BY Total DESC LIMIT 5;"
#         else:
#             # Por defecto mostramos la ocupación general de todos los subgrupos
#             sql_generado = "SELECT NombreSubgrupoCama, COUNT(CodigoCama) as CamasOcupadas FROM Ingresos GROUP BY NombreSubgrupoCama;"

#     # 3. Ejecutamos el SQL (Ya sea el de Gemini o el de contingencia)
#     try:
#         df_resultados = pd.read_sql_query(sql_generado, conn)
#         resultados_datos = df_resultados.to_dict(orient="records")
#         conn.close()
        
#         return {
#             "pregunta_recibida": request.pregunta,
#             "sql_ejecutado": sql_generado,
#             "resultados": resultados_datos,
#             "recomendacion_agente": origen_respuesta,
#             "grafico_sugerido": "table"
#         }
#     except Exception as e_sql:
#         conn.close()
#         raise HTTPException(status_code=500, detail=f"Error en BD: {str(e_sql)}")



# ---plan b
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import pandas as pd
import os
import google.generativeai as genai
from passlib.context import CryptContext
from dotenv import load_dotenv # 1. Importar dotenv

# 2. Cargar las variables del archivo .env
load_dotenv()

app = FastAPI()

# Habilitar CORS para que React (Frontend) pueda comunicarse sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Configuración de Gemini leyendo desde el .env
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise RuntimeError("No se encontró GEMINI_API_KEY en el archivo .env")

genai.configure(api_key=gemini_api_key)
# Instanciar el modelo
model = genai.GenerativeModel('gemini-1.5-flash')

class QueryRequest(BaseModel):
    pregunta: str

# Configuración de encriptación Bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginData(BaseModel):
    username: str
    password: str

# Función utilitaria para cuando quieras insertar un usuario de prueba en la base de datos
def obtener_hash_password(password):
    return pwd_context.hash(password)

@app.get("/api/dashboard")
def obtener_dashboard():
    try:
        conn = sqlite3.connect('hospital.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Datos para el Gráfico de Triage
        cursor.execute("SELECT clasificacion_triage as nombre, COUNT(*) as valor FROM Triage GROUP BY clasificacion_triage")
        triage_data = [dict(row) for row in cursor.fetchall()]

        # 2. Datos para la Tabla de Últimos Ingresos
        cursor.execute("SELECT id, tipo_servicio, fecha_ingreso FROM Ingresos ORDER BY id DESC LIMIT 4")
        ingresos_data = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return {
            "triage": triage_data,
            "ingresos": ingresos_data
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/login")
def login(datos: LoginData):
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    # Buscamos al usuario por su username
    cursor.execute("SELECT id, username, password_hash, rol FROM Usuarios WHERE username = ?", (datos.username,))
    usuario = cursor.fetchone()
    conn.close()

    # Validamos si existe y si la contraseña coincide con el Hash encriptado
    if not usuario or not pwd_context.verify(datos.password, usuario[2]):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    # Si es exitoso, devolvemos los datos (sin el hash)
    return {
        "mensaje": "Login exitoso",
        "usuario": {
            "id": usuario[0],
            "username": usuario[1],
            "rol": usuario[3] # 'admin' o 'user'
        }
    }

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