


# import sqlite3
# import pandas as pd
# import os

# def cargar_dataset_a_sqlite():
#     conn = sqlite3.connect('hospital.db')
    
#     # Ruta exacta según tu captura de pantalla
#     ruta_dataset = r'C:\Users\ASUS\Documents\Hack4Life---Hackaton\Datos\Datos'  # Asegúrate de que esta ruta sea correcta
    
#     # Tus archivos convertidos a CSV
#     archivos = [
#         'Atencion.xlsx',
#         'Ingresos.xlsx',
#         'MedicamentoInsumo.xlsx',
#         'Paciente.xlsx',
#         'ProgramacionCirugia.xlsx',
#         'Servicios.xlsx',
#         'Triage.xlsx'
#     ]
    
#     for archivo in archivos:
#         ruta_completa = os.path.join(ruta_dataset, archivo)
#         if os.path.exists(ruta_completa):
#             nombre_tabla = archivo.replace('.csv', '') 
#             print(f"Cargando {archivo} en la tabla {nombre_tabla}...")
            
#             # Sistema a prueba de fallos para probar diferentes separadores de Excel
#             separadores = [';', ',', '|']
#             cargado = False
            
#             for sep in separadores:
#                 try:
#                     df = pd.read_csv(ruta_completa, sep=sep, encoding='utf-8')
#                     # Validar que sí separó las columnas correctamente
#                     if len(df.columns) > 1:
#                         df.to_sql(nombre_tabla, conn, if_exists='replace', index=False)
#                         print(f"✅ {nombre_tabla} cargada exitosamente con {len(df)} registros.")
#                         cargado = True
#                         break
#                 except Exception:
#                     continue
                    
#             if not cargado:
#                 print(f"❌ Error: No se pudo leer {archivo}. Verifica que esté guardado como CSV delimitado por comas.")
#         else:
#             print(f"⚠️ Archivo no encontrado: {ruta_completa}")

#     conn.close()
#     print("Migración de datos reales completada.")

# if __name__ == "__main__":
#     cargar_dataset_a_sqlite()



import sqlite3
import pandas as pd
import os

def cargar_excel_a_sqlite():
    conn = sqlite3.connect('hospital.db')
    
    # Asegúrate de que esta ruta apunte a la carpeta donde están tus .xlsx
    ruta_dataset = r'C:\Users\ASUS\Documents\Hack4Life---Hackaton\Hack4Life---Hackaton\backend\Datos' 
    
    archivos = [
        'Atencion.xlsx',
        'Ingresos.xlsx',
        'MedicamentoInsumo.xlsx',
        'Paciente.xlsx',
        'ProgramacionCirugia.xlsx',
        'Servicios.xlsx',
        'Triage.xlsx'
    ]
    
    for archivo in archivos:
        ruta_completa = os.path.join(ruta_dataset, archivo)
        if os.path.exists(ruta_completa):
            nombre_tabla = archivo.replace('.xlsx', '') 
            print(f"Procesando {archivo} hacia la tabla {nombre_tabla}...")
            
            try:
                # Usamos read_excel en lugar de read_csv
                df = pd.read_excel(ruta_completa, engine='openpyxl')
                df.to_sql(nombre_tabla, conn, if_exists='replace', index=False)
                print(f"✅ {nombre_tabla} cargada exitosamente con {len(df)} registros.")
            except Exception as e:
                print(f"❌ Error leyendo {archivo}: {str(e)}")
        else:
            print(f"⚠️ Archivo no encontrado: {ruta_completa}")

    conn.close()
    print("¡Base de datos lista con todos los archivos Excel!")

if __name__ == "__main__":
    cargar_excel_a_sqlite()