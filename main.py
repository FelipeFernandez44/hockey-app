from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# Función para conectarse a la base
def get_db_connection():
    conn = sqlite3.connect('db/hockey.db')
    conn.row_factory = sqlite3.Row  # Para acceder por nombre
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/jugadoras')
def jugadoras():
    conn = get_db_connection()
    jugadoras = conn.execute('SELECT * FROM jugadoras').fetchall()
    conn.close()
    return render_template('jugadoras.html', jugadoras=jugadoras)

@app.route('/entrenamientos')
def entrenamientos():
    conn = get_db_connection()
    entrenamientos = conn.execute('SELECT * FROM entrenamientos').fetchall()
    conn.close()
    return render_template('entrenamientos.html', entrenamientos=entrenamientos)

if __name__ == '__main__':
    app.run(debug=True)
