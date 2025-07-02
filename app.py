from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from utils.leer_excel import (
    buscar_fixture_equipo,
    buscar_posiciones_equipo
)

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'
USUARIOS_FILE = 'data/usuarios.json'

def cargar_usuarios():
    if not os.path.exists(USUARIOS_FILE):
        return []
    with open(USUARIOS_FILE, 'r') as f:
        return json.load(f)

def guardar_usuarios(usuarios):
    with open(USUARIOS_FILE, 'w') as f:
        json.dump(usuarios, f, indent=2)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    equipos = ['Everton', 'Club A', 'Club B']  # Podés traer esto de leer_excel si querés
    planes = ['gratis', 'pro', 'club']

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        club = request.form['club']
        plan = request.form['plan']

        usuarios = cargar_usuarios()
        if any(u['username'] == username for u in usuarios):
            error = 'El usuario ya existe'
        else:
            usuarios.append({'username': username, 'password': password, 'club': club, 'plan': plan})
            guardar_usuarios(usuarios)
            return redirect(url_for('login'))

    return render_template('register.html', error=error, equipos=equipos, planes=planes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        usuarios = cargar_usuarios()
        user = next((u for u in usuarios if u['username'] == username and u['password'] == password), None)

        if user:
            session['username'] = user['username']
            session['club'] = user['club']
            session['plan'] = user['plan']
            return redirect(url_for('dashboard'))
        else:
            error = 'Usuario o contraseña incorrectos'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

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
        username=session['username'],
        club=equipo,
        plan=session['plan'],
        next_match=next_match,
        positions=posiciones
    )

@app.route('/')
def index():
    return redirect(url_for('login'))
