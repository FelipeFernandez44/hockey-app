import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def crear_tablas_si_no_existen():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", 5432)
        )
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            dni TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL,
            fecha_nac DATE NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            club TEXT NOT NULL,
            rama TEXT NOT NULL,
            plan TEXT NOT NULL
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
