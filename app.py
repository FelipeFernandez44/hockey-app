from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

def get_fixtures_connection():
    conn = sqlite3.connect('data/fixtures.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_usuarios_connection():
    conn = sqlite3.connect('db/hockey.db')
    conn.row_factory = sqlite3.Row
    return conn

def guardar_usuario_db(dni, nombre, fecha_nac, password, club, plan, rama):
    try:
        conn = get_usuarios_connection()
        conn.execute(
            'INSERT INTO usuarios (dni, nombre, fecha_nac, password, club, plan, rama) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (dni, nombre, fecha_nac, password, club, plan, rama)
        )
        conn.commit()
        print("✅ Usuario guardado correctamente.")
    except Exception as e:
        print(f"❌ ERROR al guardar usuario: {e}")
        raise
    finally:
        conn.close()


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

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    planes = ['gratis', 'pro', 'club']

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
        rama = request.form['rama'].upper()

        if buscar_usuario_db(dni):
            error = 'El usuario ya existe'
        else:
            guardar_usuario_db(dni, nombre, fecha_nac, password, club, plan, rama)
            flash("Usuario creado correctamente", "success")
            return redirect(url_for('login'))

    return render_template('register.html', error=error, equipos=sorted(equipos), planes=planes)

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
            session['rama'] = user['rama']
            return redirect(url_for('dashboard'))
        else:
            error = 'Usuario o contraseña incorrectos'

    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    equipo = session['club']
    categoria = session['rama']
    conn = get_fixtures_connection()

    partido = conn.execute(
        """
        SELECT * FROM fixture
        WHERE Año = 2025 AND Categoria = ? AND ( `Equipo A` = ? OR `Equipo B` = ? )
        ORDER BY Ronda ASC, Zona ASC, Fecha ASC
        LIMIT 1
        """,
        (categoria, equipo, equipo)
    ).fetchone()

    next_match = {
        "rival": partido["Equipo B"] if partido and partido["Equipo A"] == equipo else partido["Equipo A"] if partido else "N/A",
        "fecha": f"Ronda {partido['Ronda']} | Zona {partido['Zona']} | Fecha {partido['Fecha']}" if partido else "N/A"
    }

    posiciones = []
    if partido:
        ronda = partido["Ronda"]
        zona = partido["Zona"]

        posiciones_all = conn.execute(
            """
            SELECT Posiciones AS pos, Equipos AS equipo, Ptos AS pts
            FROM posiciones
            WHERE Año = 2025 AND Categoria = ? AND Ronda = ? AND Zona = ?
            ORDER BY Posiciones ASC
            """,
            (categoria, ronda, zona)
        ).fetchall()

        top = posiciones_all[:5]
        equipo_pos = next((p for p in posiciones_all if p["equipo"] == equipo), None)

        if equipo_pos and equipo_pos not in top:
            top = posiciones_all[:4] + [equipo_pos]

        posiciones = top

    conn.close()

    return render_template(
        'dashboard.html',
        username=session['nombre'],
        club=equipo,
        plan=session['plan'],
        next_match=next_match,
        positions=posiciones
    )

@app.route('/jugadoras')
def jugadoras():
    conn = get_usuarios_connection()
    jugadoras = conn.execute("SELECT * FROM jugadoras").fetchall()
    conn.close()
    return render_template('jugadoras.html', jugadoras=jugadoras)

@app.route('/entrenamientos')
def entrenamientos():
    conn = get_usuarios_connection()
    entrenamientos = conn.execute("SELECT * FROM entrenamientos").fetchall()
    conn.close()
    return render_template('entrenamientos.html', entrenamientos=entrenamientos)

@app.route('/fixture')
def fixture():
    conn = get_fixtures_connection()
    fixture = conn.execute(
        "SELECT * FROM fixture WHERE Año = 2025 ORDER BY Ronda, Zona, Fecha"
    ).fetchall()
    conn.close()
    return render_template('fixture_excel.html', fixture=fixture)

@app.route('/')
def index():
    return redirect(url_for('login'))
