import sqlite3
from pathlib import Path

# Crear carpeta si no existe
Path("db").mkdir(exist_ok=True)

# Conectarse a la base (si no existe, se crea)
conn = sqlite3.connect("db/hockey.db")
cursor = conn.cursor()

# Crear tabla usuarios
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  dni TEXT NOT NULL,
  nombre TEXT NOT NULL,
  fecha_nac TEXT NOT NULL,
  email TEXT NOT NULL,
  password TEXT NOT NULL,
  club TEXT NOT NULL,
  rama TEXT NOT NULL,
  plan TEXT NOT NULL
)
''')

# Crear tabla jugadoras
cursor.execute('''
CREATE TABLE IF NOT EXISTS jugadoras (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT,
  dni TEXT,
  telefono TEXT,
  fecha_nac TEXT,
  numero INTEGER,
  posicion TEXT,
  categoria TEXT
)
''')

# Crear tabla entrenamientos
cursor.execute('''
CREATE TABLE IF NOT EXISTS entrenamientos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fecha TEXT,
  categoria TEXT
)
''')

# Crear tabla asistencias
cursor.execute('''
CREATE TABLE IF NOT EXISTS asistencias (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entrenamiento_id INTEGER,
  jugadora_id INTEGER,
  presente BOOLEAN,
  FOREIGN KEY (entrenamiento_id) REFERENCES entrenamientos(id),
  FOREIGN KEY (jugadora_id) REFERENCES jugadoras(id)
)
''')

# Guardar y cerrar
conn.commit()
conn.close()

print("✅ Base de datos creada con las tablas.")
