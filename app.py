from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from utils.leer_excel import (
    buscar_fixture_equipo,
    buscar_posiciones_equipo
)

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Conexión a DB
def get_db_connection():
    conn = sqlite3.connect('db/hockey.db')
    conn.row_factory = sqlite3.Row
    return conn

# Guardar nuevo usuario
def guardar_usuario_db(dni, nombre, fecha_nac, password, club, plan):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO usuarios (dni, nombre, fecha_nac, password, club, plan) VALUES (?, ?, ?, ?, ?, ?)',
        (dni, nombre, fecha_nac, password, club, plan)
    )
    conn.commit()
    conn.close()

# Buscar usuario
def buscar_usuario_db(dni, password=None):
    conn = get_db_connection()
    if password:
        user = conn.execute(
            'SELECT * FROM usuarios WHERE dni = ? AND password = ?',
            (dni, password)
        ).fetchone()
    else:
        user = conn.execute(
            'SELECT * FROM usuarios WHERE dni = ?',
            (dni,)
        ).fetchone()
    conn.close()
    return user

# Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    equipos = ['Everton', 'Club A', 'Club B']
    planes = ['gratis', 'pro', 'club']

    if request.method == 'POST':
        dni = request.form['dni']
        nombre = request.form['nombre']
        fecha_nac = request.form['fecha_nac']
        password = request.form['password']
        club = request.form['club']
        plan = request.form['plan']

        if buscar_usuario_db(dni):
            error = 'El usuario ya existe'
        else:
            guardar_usuario_db(dni, nombre, fecha_nac, password, club, plan)
            return redirect(url_for('login'))

    return render_template('register.html', error=error, equipos=equipos, planes=planes)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        dni = request.form['dni']  # Cambiá el form para que el name sea dni
        password = request.form['password']

        print("🎯 Intentando login con:", dni, password)  # Log para debug

        user = buscar_usuario_db(dni, password)
        if user:
            session['username'] = user['dni']
            session['nombre'] = user['nombre']
            session['club'] = user['club']
            session['plan'] = user['plan']
            return redirect(url_for('dashboard'))
        else:
            error = 'Usuario o contraseña incorrectos'

    return render_template('login.html', error=error)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    equipo = session['club']
    ruta_excel = "data/Fixtures Unificados listo.xlsx"

    partidos = buscar_fixture_equipo(ruta_excel, equipo, "2025", "femenino", "primera")
    posiciones = buscar_posiciones_equipo(ruta_excel, equipo, "2025", "primera")

    next_match = partidos[0] if partidos else {"rival": "N/A", "fecha": "N/A"}

    return render_template(
        'dashboard.html',
        username=session['nombre'],
        club=equipo,
        plan=session['plan'],
        next_match=next_match,
        positions=posiciones
    )

@app.route('/')
def index():
    return redirect(url_for('login'))
