from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Conexión a DB de fixtures
def get_fixtures_connection():
    conn = sqlite3.connect('data/fixtures.db')
    conn.row_factory = sqlite3.Row
    return conn

# Conexión a DB de usuarios
def get_usuarios_connection():
    conn = sqlite3.connect('db/hockey.db')
    conn.row_factory = sqlite3.Row
    return conn

# Guardar nuevo usuario
def guardar_usuario_db(dni, nombre, fecha_nac, password, club, plan):
    conn = get_usuarios_connection()
    conn.execute(
        'INSERT INTO usuarios (dni, nombre, fecha_nac, password, club, plan) VALUES (?, ?, ?, ?, ?, ?)',
        (dni, nombre, fecha_nac, password, club, plan)
    )
    conn.commit()
    conn.close()

# Buscar usuario
def buscar_usuario_db(dni, password=None):
    conn = get_usuarios_connection()
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
    planes = ['gratis', 'pro', 'club']

    # Cargamos los equipos del fixture
    conn = get_fixtures_connection()
    equipos_a = conn.execute("SELECT DISTINCT `Equipo A` FROM fixture").fetchall()
    equipos_b = conn.execute("SELECT DISTINCT `Equipo B` FROM fixture").fetchall()
    conn.close()

    equipos = set([row["Equipo A"] for row in equipos_a] + [row["Equipo B"] for row in equipos_b])

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
            flash("Usuario creado correctamente", "success")
            return redirect(url_for('login'))

    return render_template('register.html', error=error, equipos=sorted(equipos), planes=planes)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        dni = request.form['dni']
        password = request.form['password']

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
    conn = get_fixtures_connection()

    # Próximo partido
    partido = conn.execute(
        "SELECT * FROM fixture WHERE `Equipo A` = ? OR `Equipo B` = ? ORDER BY Fecha LIMIT 1",
        (equipo, equipo)
    ).fetchone()

    # Posiciones
    posiciones = conn.execute(
        "SELECT `Posiciones`, `Equipos`, `Ptos` FROM posiciones WHERE 1 ORDER BY Posiciones LIMIT 10"
    ).fetchall()

    conn.close()

    next_match = {
        "rival": partido["Equipo B"] if partido and partido["Equipo A"] == equipo else partido["Equipo A"] if partido else "N/A",
        "fecha": partido["Fecha"] if partido else "N/A"
    }

    return render_template(
        'dashboard.html',
        username=session['nombre'],
        club=equipo,
        plan=session['plan'],
        next_match=next_match,
        positions=posiciones
    )

# Botones provisorios
@app.route('/jugadoras')
def jugadoras():
    return "<h1>Página de jugadoras en construcción</h1>"

@app.route('/entrenamientos')
def entrenamientos():
    return "<h1>Página de entrenamientos en construcción</h1>"

@app.route('/fixture')
def fixture():
    return "<h1>Página de fixture en construcción</h1>"

@app.route('/')
def index():
    return redirect(url_for('login'))
