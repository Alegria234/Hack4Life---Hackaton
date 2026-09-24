import os
import sqlite3
import importlib
from typing import Optional
from pathlib import Path
import pandas as pd

genai = importlib.import_module("google.generativeai")

from SecurityManager import SecurityManager
from QueryEngine import QueryEngine

class AIService:
    def __init__(self, db_name=None, key: Optional[str] = None):
        self.key = key or os.getenv("GEMINI_API_KEY")

        if not self.key:
            raise ValueError("❌ No se encontró la API Key en las variables de entorno.")

        BASE_DIR = Path(__file__).resolve().parent.parent
        self.db_path = str(db_name) if db_name else str(BASE_DIR / "data" / "hospital.db")

        self.query_engine = QueryEngine(self.db_path)
        
        genai.configure(api_key=self.key)
        self.model = genai.GenerativeModel('gemini-3.6-flash')
        
        self.esquema_bd = """
        Base de datos SQLite con las siguientes tablas y sus columnas exactas:
            - Atencion(OidIngreso, FechaAtencion)
            - Ingresos(OidIngreso, ConsecutivoIngreso, IdPaciente, ClaseIngreso, ViaIngreso, TipoRiesgo, FechaIngreso, FechaHospitalizacion, OidTriageA, CodigoCama, NombreCama, NombreGrupoCama, NombreSubgrupoCama, CodigoDiagnostico, NombreDiagnostico)
            - MedicamentoInsumo(OidIngreso, CodigoServicio, NombreServicio, Cantidad, FechaPrestacion, AreaServicio, Especialidad, OidMI)
            - Paciente(TipoDocumento, IdPaciente, NombrePaciente, FechaNacimiento, Sexo, Asegurador, Regimen, Departamento, Municipio, Zona)
            - ProgramacionCirugia(ConsecutivoProgramacion, IdPaciente, OidIngreso, CodigoServicio)
            - Servicios(OidIngreso, CodigoServicio, NombreServicio, Cantidad, FechaPrestacion, CodigoAreaServicio, AreaServicio, Especialidad, OidS)
            - Triage(OidTriage, FechaTriage, MotivoConsulta, TensionArterial, FrecuenciaCardiaca, FrecuenciaRespiratoria, Temperatura, IdPaciente2, CodigoTriage, ClasificacionTriage)
        """

    def ejecutar_consulta_conversacional(self, pregunta: str) -> dict:
        respuesta_bloqueo = self.query_engine.evaluar_seguridad_pregunta(pregunta)
        if respuesta_bloqueo:
            return respuesta_bloqueo

        pregunta_lower = pregunta.lower()

        instrucciones = f"""
            Eres un analista de datos de un hospital experto en SQLite.
            
            1. Si el usuario saluda o realiza una pregunta casual (ej: "hola", "quién eres"), responde de forma amable con el prefijo "TEXTO:".
            2. Si la pregunta requiere datos, devuelve EXCLUSIVAMENTE una consulta SQL válida que responda a la pregunta.
            
            Esquema: {self.esquema_bd}
            
            Reglas CRÍTICAS:
            - Para ocupación o estado de camas, cuenta 'CodigoCama' en la tabla 'Ingresos'.
            - Busca en 'NombreSubgrupoCama' usando LIKE.
            
            Pregunta del usuario: {pregunta_lower}
        """

        try:
            respuesta_ia = self.model.generate_content(instrucciones)
            texto_bruto = respuesta_ia.text.strip()

            if texto_bruto.startswith("TEXTO:"):
                mensaje = texto_bruto.replace("TEXTO:", "").strip()
                return {
                    "pregunta_recibida": pregunta,
                    "sql_ejecutado": "N/A - Conversacional",
                    "resultados": [{"Respuesta": mensaje}],
                    "recomendacion_agente": "Generado por Gemini IA",
                    "grafico_sugerido": "text"
                }

            sql_bruto = texto_bruto.replace("sql", "").replace("```", "").strip()
            sql_generado = SecurityManager.validar_sql_seguro(sql_bruto)
            origen_respuesta = "Generado dinámicamente por Gemini IA"

        except Exception as e:
            print(f"⚠️ Alerta API: {e}. Activando contingencia.")
            origen_respuesta = "Generado por Contingencia (Filtro de Seguridad / Límite de API)"
            sql_generado = self.query_engine.obtener_sql_contingencia(pregunta)

        return self.query_engine.ejecutar_sql_y_formatear(sql_generado, pregunta, origen_respuesta)

    def obtener_alertas_sistema(self) -> dict:
        conn = sqlite3.connect(self.db_path)
        alertas = []

        try:
            sql_camas = """
                SELECT NombreSubgrupoCama, COUNT(*) as TotalPacientes
                FROM Ingresos
                WHERE NombreSubgrupoCama IS NOT NULL AND NombreSubgrupoCama != ''
                GROUP BY NombreSubgrupoCama
                HAVING TotalPacientes > 50
                ORDER BY TotalPacientes DESC;
            """
            df_camas = pd.read_sql_query(sql_camas, conn)
            
            for _, row in df_camas.iterrows():
                alertas.append({
                    "tipo": "CAMAS",
                    "nivel": "CRITICO" if row["TotalPacientes"] > 500 else "ADVERTENCIA",
                    "area": str(row["NombreSubgrupoCama"]),
                    "mensaje": f"Saturación de ocupación en {row['NombreSubgrupoCama']}: {row['TotalPacientes']} ingresos.",
                    "valor": int(row["TotalPacientes"])
                })

            conn.close()
            return {"total_alertas": len(alertas), "alertas": alertas}
        except Exception as e:
            if conn:
                conn.close()
            return {"total_alertas": 0, "alertas": [], "error": str(e)}