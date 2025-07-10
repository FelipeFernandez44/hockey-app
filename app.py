import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from dotenv import load_dotenv
import sqlite3
from crear_tablas import crear_tablas_si_no_existen
from utils.leer_excel import obtener_equipos_disponibles

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

def conectar_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432)
    )

def get_fixtures_connection():
    conn = sqlite3.connect('data/fixtures.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return redirect(url_for('login'))

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
            session['categoria'] = user[7] if len(user) > 7 else 'general'
            session['club'] = user[6]
            session['rama'] = user[7]
            return redirect(url_for('dashboard'))
        else:
            return 'Usuario o contraseña incorrectos'

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    planes_disponibles = ['gratis', 'pro', 'premium']
    equipos_disponibles = obtener_equipos_disponibles("data/Fixtures Unificados listo.xlsx")

    if request.method == 'POST':
        datos = {key: request.form[key] for key in ['dni', 'nombre', 'fecha_nac', 'email', 'password', 'club', 'rama']}
        plan = request.form.get('plan', 'gratis')

        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO usuarios (dni, nombre, fecha_nac, email, password, club, rama, plan)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (*datos.values(), plan))
            conn.commit()
            cur.close()
            conn.close()
            flash('Usuario registrado con éxito. Iniciá sesión.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            error = f"Error al registrar: {e}"
            return render_template('register.html', planes=planes_disponibles, equipos=equipos_disponibles, error=error)

    return render_template('register.html', planes=planes_disponibles, equipos=equipos_disponibles)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    categoria = session.get('categoria')
    club = session.get('club')
    rama = session.get('rama')

    conn = get_fixtures_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM fixture
        WHERE `Equipo A` = ? AND Categoria = ? AND Rama = ?
        ORDER BY Fecha ASC
        LIMIT 1
    """, (club, categoria, rama))
    row = cur.fetchone()
    cur.close()
    conn.close()

    next_match = {
        'fecha': row['Fecha'],
        'rival': row['Equipo B'],
        'hora': row['Hora'],
        'cancha': row['Cancha']
    } if row else None

    return render_template('dashboard.html', categoria=categoria, next_match=next_match)

@app.route('/agregar_equipo', methods=['GET', 'POST'])
def agregar_equipo():
    conn = get_fixtures_connection()
    equipos_a = conn.execute("SELECT DISTINCT `Equipo A`, Rama FROM fixture").fetchall()
    equipos_b = conn.execute("SELECT DISTINCT `Equipo B`, Rama FROM fixture").fetchall()
    conn.close()

    equipos_todos = set((row[0].strip(), row[1].strip()) for row in equipos_a + equipos_b)
    categorias = ['PRIMERA', 'INTERMEDIA', '5TA', '6TA', '7MA']
    error = None

    contextos = session.get('contextos', {})
    ramas_registradas = set()
    clubes_por_rama = {}

    for ctx in contextos.values():
        rama = ctx['rama']
        club = ctx['club']
        ramas_registradas.add(rama)
        clubes_por_rama.setdefault(rama, set()).add(club)

    equipos_filtrados = set()
    for club, rama in equipos_todos:
        if rama in ramas_registradas:
            if club in clubes_por_rama[rama]:
                equipos_filtrados.add((club, rama))
        else:
            equipos_filtrados.add((club, rama))

    if request.method == 'POST':
        rama = request.form['rama'].strip().upper()
        club = request.form['club'].strip()
        categoria = request.form['categoria'].strip().upper()

        clave = f"{rama}_{club}"
        if clave in contextos:
            error = 'Ya tenés ese equipo cargado.'
        else:
            if rama in ramas_registradas and club not in clubes_por_rama[rama]:
                error = f"Ya tenés un equipo en {rama}. Solo podés agregar otra categoría del club {list(clubes_por_rama[rama])[0]}."
            else:
                contextos[clave] = {'rama': rama, 'club': club, 'categoria': categoria}
                session['contextos'] = contextos
                session['contexto_activo'] = contextos[clave]
                flash(f"✅ Nuevo equipo agregado: {rama} - {club} - {categoria}", "success")
                return redirect(url_for('dashboard'))

    return render_template(
        'agregar_equipo.html',
        equipos=list(equipos_filtrados),
        categorias=categorias,
        error=error,
        contextos=contextos,
        clubes_por_rama=clubes_por_rama
    )

@app.route('/jugadoras')
def ver_jugadoras():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM jugadoras')
    jugadoras = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('jugadoras.html', jugadoras=jugadoras)

@app.route('/entrenamientos')
def entrenamientos():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM entrenamientos')
    entrenamientos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('entrenamientos.html', entrenamientos=entrenamientos)

@app.route('/fixture')
def fixture():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM fixtures')
    fixture_data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('fixture.html', fixture=fixture_data)

@app.route('/initdb')
def init_db():
    crear_tablas_si_no_existen()
    return 'Base de datos inicializada correctamente'

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
