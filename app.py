from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from utils.leer_excel import (
    buscar_fixture_equipo,
    buscar_posiciones_equipo,
    buscar_goleadoras_equipo,
    obtener_equipos_disponibles
)

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Base de datos
def get_db_connection():
    conn = sqlite3.connect('db/hockey.db')
    conn.row_factory = sqlite3.Row
    return conn

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '1234':
            session['username'] = request.form['username']
            session['club'] = 'Everton de La Plata'
            return redirect(url_for('dashboard'))
        else:
            error = 'Usuario o contraseña incorrectos'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Ejemplo de datos dinámicos (después lo pasamos a DB / Excel)
    next_match = {
        "rival": "Club A",
        "fecha": "10/07/2025 16:00"
    }
    positions = [
        {"pos": 1, "equipo": "Everton", "pts": 25},
        {"pos": 2, "equipo": "Club A", "pts": 22},
        {"pos": 3, "equipo": "Club B", "pts": 20}
    ]

    return render_template(
        'dashboard.html',
        username=session['username'],
        club=session['club'],
        next_match=next_match,
        positions=positions
    )

# Jugadoras
@app.route('/jugadoras')
def jugadoras():
    if 'username' not in session:
        return redirect(url_for('login'))
    # Por ahora placeholder
    return "<h1>Listado de jugadoras (en construcción)</h1>"

# Entrenamientos
@app.route('/entrenamientos')
def entrenamientos():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "<h1>Listado de entrenamientos (en construcción)</h1>"

# Fixture
@app.route('/fixture')
def fixture():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "<h1>Fixture del club (en construcción)</h1>"

# Fixture desde Excel
@app.route('/fixture_excel')
def ver_fixture_excel():
    equipo = request.args.get("equipo", "").strip()
    anio = request.args.get("anio", "").strip()
    genero = request.args.get("genero", "ambos").strip().lower()
    categoria = request.args.get("categoria", "todas").strip()

    ruta = "data/Fixtures Unificados listo.xlsx"
    partidos = []
    posiciones = []
    goleadoras = []

    if equipo and anio:
        partidos = buscar_fixture_equipo(ruta, equipo, anio, genero, categoria)
        posiciones = buscar_posiciones_equipo(ruta, equipo, anio, categoria)
        torneo = partidos[0]['torneo'] if partidos else None
        zona = partidos[0]['zona'] if partidos else None
        goleadoras = buscar_goleadoras_equipo(ruta, equipo, anio, categoria, torneo, zona)

    equipos_disponibles = obtener_equipos_disponibles(ruta)

    return render_template(
        "fixture_excel.html",
        equipo=equipo,
        anio=anio,
        genero=genero,
        categoria=categoria,
        partidos=partidos,
        posiciones=posiciones,
        goleadoras=goleadoras,
        equipos_disponibles=equipos_disponibles
    )

if __name__ == '__main__':
    app.run(debug=True)
