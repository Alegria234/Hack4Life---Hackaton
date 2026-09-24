import os
import sqlite3
from typing import Optional
from pathlib import Path
import pandas as pd # type: ignore[reportMissingModuleSource]
import google.generativeai as genai # type: ignore[reportMissingModuleSource]

from SecurityManager import SecurityManager

class AIService:
    def __init__(self, db_name=None, key: Optional[str] = None):
        self.key = key or os.getenv("GEMINI_API_KEY")

        if not self.key:
            raise ValueError("❌ No se encontró la API Key, se encuentra .env")

        BASE_DIR = Path(__file__).resolve().parent.parent
        self.db_path = str(db_name) if db_name else str(BASE_DIR / "data" / "hospital.db")
        
        genai.configure(api_key=self.key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
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
        pregunta_lower = pregunta.lower()
        
        instrucciones = f"""
            Eres un analista de datos de un hospital experto en SQLite. 
            Devuelve EXCLUSIVAMENTE una consulta SQL válida que responda a la pregunta del usuario.
            No incluyas explicaciones ni formato markdown (sql). SOLO el texto de la consulta.
            
            Esquema: {self.esquema_bd}
            
            Reglas CRÍTICAS:
            - Para ocupación o estado de camas, cuenta 'CodigoCama' en la tabla 'Ingresos'.
            - Busca en 'NombreSubgrupoCama' usando LIKE.
            
            Pregunta del usuario: {pregunta_lower}
        """

        try:
            respuesta_ia = self.model.generate_content(instrucciones)
            sql_bruto = respuesta_ia.text.replace("sql", "").replace("```", "").strip()

            sql_generado = SecurityManager.validar_sql_seguro(sql_bruto)
            origen_respuesta = "Generado dinámicamente por Gemini IA"

        except Exception as e:
            print(f"⚠️ Alerta API/Seguridad: {e}. Activando contingencia automática.")
            origen_respuesta = "Generado por Contingencia (Filtro de Seguridad / Límite de API)"
            
            if "urgencias" in pregunta_lower:
                sql_generado = "SELECT NombreSubgrupoCama, COUNT(OidIngreso) as TotalPacientes FROM Ingresos WHERE NombreSubgrupoCama LIKE '%URGENCIAS%' GROUP BY NombreSubgrupoCama;"
            elif "pediatria" in pregunta_lower or "pediatría" in pregunta_lower:
                sql_generado = "SELECT NombreDiagnostico, COUNT(OidIngreso) as TotalCasos FROM Ingresos WHERE NombreSubgrupoCama LIKE '%PEDIATRIA%' GROUP BY NombreDiagnostico ORDER BY TotalCasos DESC LIMIT 5;"
            else:
                sql_generado = "SELECT NombreSubgrupoCama, COUNT(CodigoCama) as CamasOcupadas FROM Ingresos GROUP BY NombreSubgrupoCama;"

        conn = sqlite3.connect(self.db_path)

        try:
            df_resultados = pd.read_sql_query(sql_generado, conn)

            df_anonimo = SecurityManager.anonimizar_dataframe(df_resultados)

            df_limpio = df_anonimo.fillna("")
            resultados_datos = df_limpio.to_dict(orient="records")
            
            conn.close()
            
            return {
                "pregunta_recibida": pregunta,
                "sql_ejecutado": sql_generado,
                "resultados": resultados_datos,
                "recomendacion_agente": origen_respuesta,
                "grafico_sugerido": "table"
            }
        except Exception as e_sql:
            conn.close()
            raise e_sql

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

            try:
                sql_meds = """
                    SELECT NombreServicio, SUM(Cantidad) as TotalConsumido
                    FROM Servicios
                    WHERE NombreServicio IS NOT NULL
                    GROUP BY NombreServicio
                    ORDER BY TotalConsumido DESC
                    LIMIT 5;
                """
                df_meds = pd.read_sql_query(sql_meds, conn)
            except Exception:
                sql_meds = """
                    SELECT NombreServicio, SUM(Cantidad) as TotalConsumido
                    FROM MedicamentoInsumo
                    WHERE NombreServicio IS NOT NULL
                    GROUP BY NombreServicio
                    ORDER BY TotalConsumido DESC
                    LIMIT 5;
                """
                df_meds = pd.read_sql_query(sql_meds, conn)

            for _, row in df_meds.iterrows():
                cant = int(row["TotalConsumido"]) if pd.notnull(row["TotalConsumido"]) else 0
                alertas.append({
                    "tipo": "MEDICAMENTO_INSUMO",
                    "nivel": "ADVERTENCIA",
                    "area": str(row["NombreServicio"]),
                    "mensaje": f"Consumo crítico de insumo/servicio '{row['NombreServicio']}': {cant} unidades.",
                    "valor": cant
                })

            conn.close()
            return {
                "total_alertas": len(alertas),
                "alertas": alertas
            }

        except Exception as e:
            if conn:
                conn.close()
            print(f"Error calculando alertas: {e}")
            return {
                "total_alertas": 0,
                "alertas": [],
                "error": str(e)
            }