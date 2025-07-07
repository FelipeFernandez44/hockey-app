from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import sqlite3

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Conexión a PostgreSQL
import os
import psycopg2

def get_postgres_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])

# Conexión al fixture (por ahora lo dejamos en SQLite)
def get_fixtures_connection():
    conn = sqlite3.connect('data/fixtures.db')
    conn.row_factory = sqlite3.Row
    return conn

# Funciones de DB
def guardar_usuario_db(dni, nombre, fecha_nac, email, password, club, rama, plan):
    conn = get_postgres_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            '''
            INSERT INTO usuarios (dni, nombre, fecha_nac, email, password, club, rama, plan)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''',
            (dni, nombre, fecha_nac, email, password, club, rama, plan)
        )
        conn.commit()
        print("✅ Usuario guardado correctamente.")
    except Exception as e:
        print(f"❌ ERROR al guardar usuario: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def buscar_usuario_db(dni, password=None):
    conn = get_postgres_connection()
    cursor = conn.cursor()
    try:
        if password:
            cursor.execute('SELECT * FROM usuarios WHERE dni = %s AND password = %s', (dni, password))
        else:
            cursor.execute('SELECT * FROM usuarios WHERE dni = %s', (dni,))
        user = cursor.fetchone()
        if user:
            desc = [desc[0] for desc in cursor.description]
            return dict(zip(desc, user))
        else:
            return None
    finally:
        cursor.close()
        conn.close()

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
        email = request.form['email']
        password = request.form['password']
        club = request.form['club'].strip()
        rama = request.form['rama']
        plan = request.form['plan']

        if buscar_usuario_db(dni):
            error = 'El usuario ya existe'
        else:
            guardar_usuario_db(dni, nombre, fecha_nac, email, password, club, rama, plan)
            flash("Usuario creado correctamente", "success")
            return redirect(url_for('login'))

    return render_template('register.html', error=error, planes=planes, equipos=sorted(equipos))

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
            session['plan'] = user['plan']
            session['contextos'] = {}
            session['contextos'][f"{user['rama']}_{user['club']}"] = {
                'rama': user['rama'],
                'club': user['club']
            }
            session['contexto_activo'] = session['contextos'][f"{user['rama']}_{user['club']}"]
            return redirect(url_for('dashboard'))
        else:
            error = 'Usuario o contraseña incorrectos'

    return render_template('login.html', error=error)

@app.route('/jugadoras')
def jugadoras():
    conn = get_postgres_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jugadoras")
    rows = cursor.fetchall()
    desc = [d[0] for d in cursor.description]
    jugadoras = [dict(zip(desc, row)) for row in rows]
    cursor.close()
    conn.close()
    return render_template('jugadoras.html', jugadoras=jugadoras)

@app.route('/entrenamientos')
def entrenamientos():
    conn = get_postgres_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM entrenamientos")
    rows = cursor.fetchall()
    desc = [d[0] for d in cursor.description]
    entrenamientos = [dict(zip(desc, row)) for row in rows]
    cursor.close()
    conn.close()
    return render_template('entrenamientos.html', entrenamientos=entrenamientos)

@app.route('/fixture')
def fixture():
    conn = get_fixtures_connection()
    fixture = conn.execute("SELECT * FROM fixture WHERE Año = 2025 ORDER BY Ronda, Zona, Fecha").fetchall()
    conn.close()
    return render_template('fixture_excel.html', fixture=fixture)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session or not session.get('contextos'):
        return redirect(url_for('seleccionar_contexto'))

    contextos = session['contextos']
    if len(contextos) > 1 and not session.get('activo'):
        flash("Con qué equipo querés trabajar hoy?", "info")
        return render_template('elegir_equipo.html', contextos=contextos)

    if not session.get('activo'):
        session['activo'] = next(iter(contextos.items()))

    rama, data = session['activo']
    equipo = data['club']
    categoria = data['categoria']

    contexto = session['contexto_activo']
    equipo = contexto['club']
    rama = contexto['rama']

    conn = get_fixtures_connection()
    partido = conn.execute(
        """
        SELECT * FROM fixture
        WHERE Año = 2025 AND Rama = ? AND (TRIM(`Equipo A`) = ? OR TRIM(`Equipo B`) = ?)
        ORDER BY Ronda ASC, Zona ASC, Fecha ASC
        LIMIT 1
        """,
        (rama, equipo, equipo)
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
            WHERE Año = 2025 AND Ronda = ? AND Zona = ? AND Rama = ?
            ORDER BY Posiciones ASC
            """,
            (ronda, zona, rama)
        ).fetchall()

        top = posiciones_all[:5]
        equipo_pos = next((p for p in posiciones_all if p["equipo"] == equipo), None)
        if equipo_pos and equipo_pos not in top:
            top = posiciones_all[:4] + [equipo_pos]
        posiciones = top

    conn.close()
    return render_template('dashboard.html', username=session['nombre'], plan=session['plan'],
                           next_match=next_match, positions=posiciones, club=equipo)

@app.route('/seleccionar_contexto', methods=['GET', 'POST'])
def seleccionar_contexto():
    conn = get_fixtures_connection()
    equipos_a = conn.execute("SELECT DISTINCT `Equipo A`, Rama FROM fixture").fetchall()
    equipos_b = conn.execute("SELECT DISTINCT `Equipo B`, Rama FROM fixture").fetchall()
    conn.close()

    equipos = set([(row["Equipo A"], row["Rama"]) for row in equipos_a] + [(row["Equipo B"], row["Rama"]) for row in equipos_b])

    ramas = ['DAMAS', 'CABALLEROS']
    categorias = ['PRIMERA', 'INTERMEDIA', '5TA', '6TA', '7MA']

    ramas_ocupadas = set(session.get('contextos', {}).keys())

    if request.method == 'POST':
        rama = request.form['rama'].upper()
        club = request.form['club'].strip()
        categoria = request.form['categoria'].upper()

        if rama in ramas_ocupadas:
            flash(f"Ya tenés un equipo registrado en {rama}. Solo podés elegir otro de la otra rama.", "danger")
        else:
            session.setdefault('contextos', {})[rama] = {
                'club': club,
                'categoria': categoria
            }
            flash(f"Contexto guardado: {rama} - {club} - {categoria}", "success")
            return redirect(url_for('dashboard'))

    ramas_habilitadas = [r for r in ramas if r not in ramas_ocupadas]

    return render_template(
        'seleccionar_contexto.html',
        ramas=ramas_habilitadas,
        categorias=categorias,
        equipos=equipos
    )

@app.route('/agregar_equipo', methods=['GET', 'POST'])
def agregar_equipo():
    conn = get_fixtures_connection()
    equipos_a = conn.execute("SELECT DISTINCT `Equipo A`, Rama FROM fixture").fetchall()
    equipos_b = conn.execute("SELECT DISTINCT `Equipo B`, Rama FROM fixture").fetchall()
    conn.close()

    equipos = set([ (row["Equipo A"], row["Rama"]) for row in equipos_a ] + 
                  [ (row["Equipo B"], row["Rama"]) for row in equipos_b ])
    categorias = ['PRIMERA', 'INTERMEDIA', '5TA', '6TA', '7MA']

    error = None
    if request.method == 'POST':
        rama = request.form['rama']
        club = request.form['club']
        categoria = request.form['categoria']

        clave = f"{rama}_{club}"
        if clave in session['contextos']:
            error = 'Ya tenés ese equipo cargado.'
        else:
            session['contextos'][clave] = {
                'rama': rama,
                'club': club,
                'categoria': categoria
            }
            session['contexto_activo'] = session['contextos'][clave]
            flash(f"Nuevo equipo agregado: {rama} - {club} - {categoria}", "success")
            return redirect(url_for('dashboard'))

    return render_template('agregar_equipo.html', equipos=equipos, categorias=categorias, error=error)

@app.route('/set_equipo_activo', methods=['POST'])
def set_equipo_activo():
    seleccion = request.form['seleccion']
    if seleccion in session['contextos']:
        session['activo'] = (seleccion, session['contextos'][seleccion])
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('login'))
