import sqlite3
from pathlib import Path

# Crear carpeta si no existe
Path("db").mkdir(exist_ok=True)

# Crear DB
conn = sqlite3.connect("db/hockey.db")
cursor = conn.cursor()

# Tabla usuarios (sin apellido, bien limpia)
cursor.execute("""
CREATE TABLE usuarios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  dni TEXT UNIQUE NOT NULL,
  nombre TEXT NOT NULL,
  fecha_nac TEXT NOT NULL,
  password TEXT NOT NULL,
  club TEXT NOT NULL,
  rama TEXT NOT NULL,
  plan TEXT NOT NULL
  )
""")

# Tabla jugadoras
cursor.execute("""
CREATE TABLE jugadoras (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT,
  dni TEXT,
  telefono TEXT,
  fecha_nac TEXT,
  numero INTEGER,
  posicion TEXT,
  categoria TEXT
)
""")

# Tabla entrenamientos
cursor.execute("""
CREATE TABLE entrenamientos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fecha TEXT,
  categoria TEXT
)
""")

# Tabla asistencias
cursor.execute("""
CREATE TABLE asistencias (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entrenamiento_id INTEGER,
  jugadora_id INTEGER,
  presente BOOLEAN,
  FOREIGN KEY (entrenamiento_id) REFERENCES entrenamientos(id),
  FOREIGN KEY (jugadora_id) REFERENCES jugadoras(id)
)
""")

conn.commit()
conn.close()

print("✅ DB hockey.db creada correctamente.")
