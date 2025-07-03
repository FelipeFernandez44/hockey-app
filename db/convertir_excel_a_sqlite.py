import sqlite3
import pandas as pd

# Archivo de origen
excel_file = "data/Fixtures Unificados listo.xlsx"
db_file = "data/fixtures.db"

# Leemos las hojas
df_fixture = pd.read_excel(excel_file, sheet_name="Fixtures")
df_posiciones = pd.read_excel(excel_file, sheet_name="Tablas de Posiciones")
df_goleadoras = pd.read_excel(excel_file, sheet_name="Goleadoras")

# Conectamos a la DB (la sobreescribimos si ya existe)
conn = sqlite3.connect(db_file)

# Guardamos las tablas
df_fixture.to_sql("fixture", conn, if_exists="replace", index=False)
df_posiciones.to_sql("posiciones", conn, if_exists="replace", index=False)
df_goleadoras.to_sql("goleadoras", conn, if_exists="replace", index=False)

# Creamos la tabla usuarios si no existe
conn.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    dni TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    fecha_nac TEXT NOT NULL,
    password TEXT NOT NULL,
    club TEXT NOT NULL,
    plan TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("✅ ¡La base fixtures.db fue generada exitosamente!")
