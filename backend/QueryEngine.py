import sqlite3
import pandas as pd  # type: ignore[reportMissingModuleSource]
from SecurityManager import SecurityManager

class QueryEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def evaluar_seguridad_pregunta(self, pregunta: str) -> dict | None:
        pregunta_lower = pregunta.lower()

        # Detección de Intentos de Inyección SQL
        patrones_sqli = ["' or", "'or", "union select", "drop table", "drop database", "insert into", "delete from", "--", ";"]
        if any(patron in pregunta_lower for patron in patrones_sqli):
            return {
                "pregunta_recibida": pregunta,
                "sql_ejecutado": "N/A - Bloqueado por SecurityManager",
                "resultados": [{"Alerta_Seguridad": "🛡️ Intento de Inyección SQL neutralizado por SecurityManager. La consulta ha sido descartada."}],
                "recomendacion_agente": "Filtro de Seguridad Activo (SQLi Prevented)",
                "grafico_sugerido": "table"
            }

        # Detección de Extracción de Datos Personales (PII / HIPAA)
        patrones_pii = [
            "nombre completo", "cedula", "cédula", "identificacion", 
            "documento", "nombre del paciente", "quien es el paciente", 
            "paciente en la cama", "cama "
        ]
        if any(patron in pregunta_lower for patron in patrones_pii):
            return {
                "pregunta_recibida": pregunta,
                "sql_ejecutado": "N/A - Bloqueado por Política PII/HIPAA",
                "resultados": [{"Privacidad_HIPAA": "⚠️ Acceso Restringido: Por normativas de privacidad y anonimización de datos (HIPAA), no es posible consultar datos de identificación individual. Solo se proveen métricas agregadas."}],
                "recomendacion_agente": "Protección de Privacidad de Datos",
                "grafico_sugerido": "table"
            }

        return None

    def obtener_sql_contingencia(self, pregunta: str) -> str:
        pregunta_lower = pregunta.lower()

        if "uci" in pregunta_lower or ("cama" in pregunta_lower and "disponible" in pregunta_lower):
            return """
                SELECT NombreSubgrupoCama, COUNT(CodigoCama) as CamasOcupadas
                FROM Ingresos 
                WHERE NombreSubgrupoCama LIKE '%UCI%' OR NombreSubgrupoCama LIKE '%INTENSIV%'
                GROUP BY NombreSubgrupoCama ORDER BY CamasOcupadas DESC;
            """
        elif "alta" in pregunta_lower:
            return """
                SELECT NombreSubgrupoCama, COUNT(OidIngreso) as TotalAltasRegistradas
                FROM Ingresos 
                WHERE ClaseIngreso LIKE '%ALTA%' OR ViaIngreso LIKE '%ALTA%' OR NombreSubgrupoCama IS NOT NULL
                GROUP BY NombreSubgrupoCama ORDER BY TotalAltasRegistradas DESC LIMIT 5;
            """
        elif "urgencias" in pregunta_lower:
            return """
                SELECT NombreSubgrupoCama, COUNT(OidIngreso) as TotalPacientesAtendidos
                FROM Ingresos 
                WHERE NombreSubgrupoCama LIKE '%URGENCIAS%'
                GROUP BY NombreSubgrupoCama ORDER BY TotalPacientesAtendidos DESC;
            """
        elif "pediatria" in pregunta_lower or "pediatría" in pregunta_lower:
            return """
                SELECT NombreDiagnostico, COUNT(OidIngreso) as TotalCasos
                FROM Ingresos 
                WHERE NombreSubgrupoCama LIKE '%PEDIATRIA%' AND NombreDiagnostico IS NOT NULL
                GROUP BY NombreDiagnostico ORDER BY TotalCasos DESC LIMIT 5;
            """
        elif any(k in pregunta_lower for k in ["medicamento", "stock", "insumo", "farmacia"]):
            return """
                SELECT NombreServicio as Medicamento_Insumo, SUM(Cantidad) as UnidadesConsumidas
                FROM Servicios 
                WHERE NombreServicio IS NOT NULL
                GROUP BY NombreServicio ORDER BY UnidadesConsumidas DESC LIMIT 5;
            """
        elif "triage" in pregunta_lower:
            return """
                SELECT ClasificacionTriage, COUNT(*) as TotalPacientesClasificados
                FROM Triage 
                WHERE ClasificacionTriage IS NOT NULL AND ClasificacionTriage != ''
                GROUP BY ClasificacionTriage ORDER BY TotalPacientesClasificados DESC;
            """
        elif "cirug" in pregunta_lower:
            return """
                SELECT CodigoServicio as Procedimiento_Quirurgico, COUNT(*) as TotalCirugiasProgramadas
                FROM ProgramacionCirugia 
                GROUP BY CodigoServicio ORDER BY TotalCirugiasProgramadas DESC LIMIT 5;
            """
        else:
            return """
                SELECT NombreSubgrupoCama, COUNT(CodigoCama) as TotalCamasRegistradas
                FROM Ingresos 
                WHERE NombreSubgrupoCama IS NOT NULL AND NombreSubgrupoCama != ''
                GROUP BY NombreSubgrupoCama ORDER BY TotalCamasRegistradas DESC LIMIT 7;
            """

    def ejecutar_sql_y_formatear(self, sql_query: str, pregunta: str, origen: str) -> dict:
        conn = sqlite3.connect(self.db_path)
        try:
            df_resultados = pd.read_sql_query(sql_query, conn)
            conn.close()

            df_anonimo = SecurityManager.anonimizar_dataframe(df_resultados)
            resultados_datos = df_anonimo.fillna("").to_dict(orient="records")

            return {
                "pregunta_recibida": pregunta,
                "sql_ejecutado": sql_query.strip(),
                "resultados": resultados_datos,
                "recomendacion_agente": origen,
                "grafico_sugerido": "table"
            }
        except Exception as e:
            if conn:
                conn.close()
            raise e