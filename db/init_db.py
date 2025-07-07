import psycopg2
import os

def crear_tablas_si_no_existen():
    try:
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            dni TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL,
            password TEXT NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jugadoras (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            dni TEXT UNIQUE,
            fecha_nacimiento DATE,
            posicion TEXT,
            numero INTEGER,
            equipo TEXT
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS entrenamientos (
            id SERIAL PRIMARY KEY,
            equipo TEXT NOT NULL,
            fecha DATE NOT NULL,
            horario TEXT,
            asistentes TEXT
        );
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Tablas creadas o ya existentes.")
    except Exception as e:
        print("❌ Error al crear las tablas:", e)
