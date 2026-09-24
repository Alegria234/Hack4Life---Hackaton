import re
import pandas as pd  # type: ignore[reportMissingModuleSource]
import numpy as np

class SecurityManager:

    FORBIDDEN_KEYWORDS = [
        r"\bDROP\b", r"\bDELETE\b", r"\bUPDATE\b", r"\bINSERT\b", 
        r"\bALTER\b", r"\bTRUNCATE\b", r"\bCREATE\b", r"\bEXEC\b"
    ]

    PII_COLUMNS = ['nombrepaciente', 'idpaciente', 'idpaciente2', 'tipodocumento']

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