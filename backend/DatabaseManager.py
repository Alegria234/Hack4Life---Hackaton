import os
import sqlite3
from pathlib import Path
import pandas as pd  # type: ignore[reportMissingModuleSource]

class DatabaseManager:
    def __init__(self, db_name=None, ruta_dataset=None):
        BASE_DIR = Path(__file__).resolve().parent.parent
        
        self.db_path = str(db_name) if db_name else str(BASE_DIR / "data" / "hospital.db")
        self.ruta_dataset = str(ruta_dataset) if ruta_dataset else str(BASE_DIR / "data" / "hospital.db")
        
        self.archivos = [
            'Atencion.xlsx',
            'Ingresos.xlsx',
            'MedicamentoInsumo.xlsx',
            'Paciente.xlsx',
            'ProgramacionCirugia.xlsx',
            'Servicios.xlsx',
            'Triage.xlsx'
        ]

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _get_path(self) -> str:
        return self.ruta_dataset

    def init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Tabla 1: Admisiones
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Admisiones (
                id_paciente INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_ingreso TEXT,
                fecha_salida TEXT,
                servicio TEXT,
                diagnostico TEXT,
                triage INTEGER,
                medico_asignado TEXT
            )
            ''')

            # Tabla 2: Camas
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Camas (
                id_cama INTEGER PRIMARY KEY AUTOINCREMENT,
                servicio TEXT,
                estado TEXT,
                id_paciente INTEGER,
                FOREIGN KEY (id_paciente) REFERENCES Admisiones(id_paciente)
            )
            ''')

            # Tabla 3: Medicamentos
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Medicamentos (
                id_medicamento INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                stock INTEGER,
                fecha_vencimiento TEXT,
                consumo_diario_promedio REAL
            )
            ''')
            
            conn.commit()
        print(f"✅ Base de datos {self.db_path} y sus Tablas fueron correctamente estructuradas")

    def _tabla_existe(self, conn, nombre_tabla: str) -> bool:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", 
            (nombre_tabla,)
        )
        return cursor.fetchone()[0] == 1

    def archivosSaltantes(self) -> bool:
        if not os.path.exists(self.ruta_dataset) or not os.listdir(self.ruta_dataset):
            print(f"❌ Error: La ruta '{self.ruta_dataset}' no existe o está vacía.")
            return False

        archivos_faltantes = [
            f for f in self.archivos 
            if not os.path.exists(os.path.join(self.ruta_dataset, f))
        ]

        if archivos_faltantes:
            print(f"⚠️ Archivos no encontrados: {', '.join(archivos_faltantes)}")
            return False

        return True
    
    def cargar_excel_a_sqlite(self, confirmar_sobrescribir=True):
        if not self.archivosSaltantes():
            return

        with self._get_connection() as conn:
            for archivo in self.archivos:
                ruta_completa = os.path.join(self.ruta_dataset, archivo)
                nombre_tabla = archivo.replace('.xlsx', '')

                df = pd.read_excel(ruta_completa, engine='openpyxl')
                if df.empty:
                    print(f"⚠️ El archivo {archivo} está vacío, se omite.")
                    continue

                df.columns = df.columns.astype(str).str.strip()

                df.to_sql(nombre_tabla, conn, if_exists='replace', index=False)
                print(f"✅ Tabla '{nombre_tabla}' cargada con {len(df)} registros.")

        print("¡Proceso de carga e ingesta finalizado con éxito!")

        ''' 
        for archivo in self.archivos:
            ruta_completa = os.path.join(self.ruta_dataset, archivo)
            
            if os.path.exists(ruta_completa):
                nombre_tabla = archivo.replace('.xlsx', '') 
                
                if self._tabla_existe(conn, nombre_tabla):
                    print(f"⚠️ La tabla '{nombre_tabla}' ya existe.")
                    if confirmar_sobrescribir:
                        print(f"🔄 Actualizando datos de '{nombre_tabla}'...")

                try:
                    df = pd.read_excel(ruta_completa, engine='openpyxl')
                    
                    if df.empty:
                        print(f"⚠️ El archivo {archivo} está vacío.")
                        continue

                    df.columns = df.columns.astype(str).str.strip()

                    df.to_sql(nombre_tabla, conn, if_exists='replace', index=False)
                    print(f"✅ {nombre_tabla} cargada con {len(df)} registros.\n")

                except Exception as e:
                    print(f"❌ Error leyendo {archivo}: {str(e)}\n")
            else:
                print(f"⚠️ Archivo no encontrado: {ruta_completa}\n")

        conn.close()
        print("¡Proceso de carga finalizado!")
        '''

if __name__ == "__main__":
    db_manager = DatabaseManager()
    db_manager.init_db()
    db_manager.cargar_excel_a_sqlite()