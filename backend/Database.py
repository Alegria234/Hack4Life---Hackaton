import sqlite3

def init_db():
    # Crea la conexión y el archivo si no existe
    conn = sqlite3.connect('hospital.db')
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
    conn.close()
    print("¡Base de datos y tablas creadas con éxito!")

if __name__ == "__main__":
    init_db()