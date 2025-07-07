import os
from flask import Flask, render_template, request, redirect, session, url_for
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

# Función para conectar a la base de datos

def conectar_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "dpg-d1m1cgripnbc73fifqa0-a"),
        database=os.getenv("DB_NAME", "hockeyapp"),
        user=os.getenv("DB_USER", "hockeyapp_user"),
        password=os.getenv("DB_PASSWORD", "TU_PASSWORD_AQUI"),
        port=os.getenv("DB_PORT", 5432)
    )

# Ruta raíz
@app.route('/')
def index():
    return redirect(url_for('login'))

# Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        dni = request.form['dni']
        nombre = request.form['nombre']
        fecha_nac = request.form['fecha_nac']
        email = request.form['email']
        password = request.form['password']
        club = request.form['club']
        rama = request.form['rama']
        plan = request.form['plan']

        conn = conectar_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM usuarios WHERE dni = %s', (dni,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return 'Usuario ya registrado'

        cur.execute('''INSERT INTO usuarios (dni, nombre, fecha_nac, email, password, club, rama, plan)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                    (dni, nombre, fecha_nac, email, password, club, rama, plan))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('login'))

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        dni = request.form['dni']
        password = request.form['password']

        conn = conectar_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM usuarios WHERE dni = %s AND password = %s', (dni, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['categoria'] = user[7] if len(user) > 7 else 'general'  # fallback
            return redirect(url_for('dashboard'))
        else:
            return 'Usuario o contraseña incorrectos'

    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    categoria = session.get('categoria')
    return render_template('dashboard.html', categoria=categoria)

# Ruta para ver jugadoras
@app.route('/jugadoras')
def ver_jugadoras():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM jugadoras')
    jugadoras = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('jugadoras.html', jugadoras=jugadoras)

# Ruta para ver entrenamientos
@app.route('/entrenamientos')
def entrenamientos():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM entrenamientos')
    entrenamientos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('entrenamientos.html', entrenamientos=entrenamientos)

# Ruta para ver fixture desde base
@app.route('/fixture')
def fixture():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM fixtures')  # Asegurate de tener esta tabla o cambiar el nombre
    fixture_data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('fixture.html', fixture=fixture_data)

# Inicializar base de datos
@app.route('/initdb')
def init_db():
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            dni TEXT,
            nombre TEXT,
            fecha_nac TEXT,
            email TEXT,
            password TEXT,
            club TEXT,
            rama TEXT,
            plan TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS jugadoras (
            id SERIAL PRIMARY KEY,
            nombre TEXT,
            dni TEXT,
            fecha_nac TEXT,
            posicion TEXT,
            numero TEXT,
            equipo TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS entrenamientos (
            id SERIAL PRIMARY KEY,
            fecha TEXT,
            equipo TEXT,
            tipo TEXT
        )
    ''')

    conn.commit()
    cur.close()
    conn.close()
    return 'Base de datos inicializada correctamente'

if __name__ == '__main__':
    app.run(debug=True)