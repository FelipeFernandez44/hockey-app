from flask import Flask, render_template, request, redirect, url_for
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

@app.route('/jugadora/<int:jugadora_id>/editar', methods=['GET', 'POST'])
def editar_jugadora(jugadora_id):
    conn = get_db_connection()
    jugadora = conn.execute('SELECT * FROM jugadoras WHERE id = ?', (jugadora_id,)).fetchone()

    if jugadora is None:
        conn.close()
        return "❌ Jugadora no encontrada", 404

    if request.method == 'POST':
        nombre = request.form['nombre']
        dni = request.form['dni']
        telefono = request.form['telefono']
        fecha_nac = request.form['fecha_nac']
        numero = request.form['numero']
        posicion = request.form['posicion']
        categoria = request.form['categoria']

        conn.execute('''
            UPDATE jugadoras
            SET nombre = ?, dni = ?, telefono = ?, fecha_nac = ?, numero = ?, posicion = ?, categoria = ?
            WHERE id = ?
        ''', (nombre, dni, telefono, fecha_nac, numero, posicion, categoria, jugadora_id))
        conn.commit()
        conn.close()
        return redirect(url_for('jugadoras'))

    conn.close()
    return render_template('editar_jugadora.html', jugadora=jugadora)

@app.route('/jugadora/<int:jugadora_id>')
def ver_jugadora(jugadora_id):
    conn = get_db_connection()

    # Buscar jugadora por ID
    jugadora = conn.execute('SELECT * FROM jugadoras WHERE id = ?', (jugadora_id,)).fetchone()

    # Si no existe, devolver error 404
    if jugadora is None:
        conn.close()
        return "❌ Jugadora no encontrada", 404

    # Obtener sus asistencias (opcional)
    asistencias = conn.execute('''
        SELECT e.fecha, e.categoria, a.presente
        FROM asistencias a
        JOIN entrenamientos e ON a.entrenamiento_id = e.id
        WHERE a.jugadora_id = ?
        ORDER BY e.fecha DESC
    ''', (jugadora_id,)).fetchall()

    # Calcular estadísticas
    total = len(asistencias)
    presentes = sum(1 for a in asistencias if a['presente'])
    ausentes = total - presentes
    porcentaje = round((presentes / total) * 100, 1) if total > 0 else 0

    conn.close()
    return render_template('jugadora.html',
                           jugadora=jugadora,
                           asistencias=asistencias,
                           presentes=presentes,
                           ausentes=ausentes,
                           porcentaje=porcentaje)

@app.route('/jugadora/nueva', methods=['GET', 'POST'])
def nueva_jugadora():
    if request.method == 'POST':
        nombre = request.form['nombre']
        dni = request.form['dni']
        telefono = request.form['telefono']
        fecha_nac = request.form['fecha_nac']
        numero = request.form['numero']
        posicion = request.form['posicion']
        categoria = request.form['categoria']

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO jugadoras (nombre, dni, telefono, fecha_nac, numero, posicion, categoria)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, dni, telefono, fecha_nac, numero, posicion, categoria))
        conn.commit()
        conn.close()

        return redirect(url_for('jugadoras'))

    return render_template('jugadora_nueva.html')

@app.route('/asistencia/<int:entrenamiento_id>', methods=['GET', 'POST'])
def tomar_asistencia(entrenamiento_id):
    conn = get_db_connection()

    entrenamiento = conn.execute('SELECT * FROM entrenamientos WHERE id = ?', (entrenamiento_id,)).fetchone()

    if entrenamiento is None:
        conn.close()
        return "❌ Entrenamiento no encontrado", 404

    if request.method == 'POST':
        jugadoras_presentes = request.form.getlist('presentes')

        # Eliminar asistencias previas (por si se corrige)
        conn.execute('DELETE FROM asistencias WHERE entrenamiento_id = ?', (entrenamiento_id,))

        for jugadora_id in request.form.getlist('jugadora_ids'):
            presente = jugadora_id in jugadoras_presentes
            conn.execute('''
                INSERT INTO asistencias (entrenamiento_id, jugadora_id, presente)
                VALUES (?, ?, ?)
            ''', (entrenamiento_id, jugadora_id, presente))

        conn.commit()
        conn.close()
        return redirect(url_for('entrenamientos'))

       # Modo GET: mostrar lista de jugadoras de esa categoría
    jugadoras = conn.execute('SELECT * FROM jugadoras WHERE categoria = ?', (entrenamiento['categoria'],)).fetchall()

    # Verificamos si ya hay asistencia cargada
    ya_registrada = conn.execute(
        'SELECT COUNT(*) as total FROM asistencias WHERE entrenamiento_id = ?', 
        (entrenamiento_id,)
    ).fetchone()['total'] > 0
    print("🎯 Ya registrada:", ya_registrada)

    conn.close()

    if ya_registrada:
        return render_template('asistencia_registrada.html', entrenamiento=entrenamiento)

    return render_template('asistencia.html', entrenamiento=entrenamiento, jugadoras=jugadoras)


@app.route('/entrenamiento/nuevo', methods=['GET', 'POST'])
def nuevo_entrenamiento():
    if request.method == 'POST':
        fecha = request.form['fecha']
        categoria = request.form['categoria']

        conn = get_db_connection()
        conn.execute('INSERT INTO entrenamientos (fecha, categoria) VALUES (?, ?)', (fecha, categoria))
        conn.commit()
        conn.close()

        return redirect(url_for('entrenamientos'))

    return render_template('entrenamiento_nuevo.html')

@app.route('/jugadora/<int:jugadora_id>/eliminar', methods=['GET', 'POST'])
def eliminar_jugadora(jugadora_id):
    conn = get_db_connection()
    jugadora = conn.execute('SELECT * FROM jugadoras WHERE id = ?', (jugadora_id,)).fetchone()

    if jugadora is None:
        conn.close()
        return "❌ Jugadora no encontrada", 404

    if request.method == 'POST':
        # Eliminamos asistencias asociadas primero para mantener integridad
        conn.execute('DELETE FROM asistencias WHERE jugadora_id = ?', (jugadora_id,))
        # Luego eliminamos la jugadora
        conn.execute('DELETE FROM jugadoras WHERE id = ?', (jugadora_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('jugadoras'))

    conn.close()
    return render_template('eliminar_jugadora.html', jugadora=jugadora)

@app.route('/entrenamiento/<int:entrenamiento_id>/editar', methods=['GET', 'POST'])
def editar_entrenamiento(entrenamiento_id):
    conn = get_db_connection()
    entrenamiento = conn.execute('SELECT * FROM entrenamientos WHERE id = ?', (entrenamiento_id,)).fetchone()

    if entrenamiento is None:
        conn.close()
        return "❌ Entrenamiento no encontrado", 404

    if request.method == 'POST':
        nueva_fecha = request.form['fecha']
        nueva_categoria = request.form['categoria']

        conn.execute('''
            UPDATE entrenamientos
            SET fecha = ?, categoria = ?
            WHERE id = ?
        ''', (nueva_fecha, nueva_categoria, entrenamiento_id))
        conn.commit()
        conn.close()

        return redirect(url_for('entrenamientos'))

    conn.close()
    return render_template('editar_entrenamiento.html', entrenamiento=entrenamiento)

@app.route('/entrenamiento/<int:entrenamiento_id>/asistencias')
def ver_asistencias_por_entrenamiento(entrenamiento_id):
    conn = get_db_connection()

    entrenamiento = conn.execute('SELECT * FROM entrenamientos WHERE id = ?', (entrenamiento_id,)).fetchone()

    if entrenamiento is None:
        conn.close()
        return "❌ Entrenamiento no encontrado", 404

    asistencias = conn.execute('''
        SELECT j.nombre, j.numero, j.posicion, a.presente
        FROM asistencias a
        JOIN jugadoras j ON a.jugadora_id = j.id
        WHERE a.entrenamiento_id = ?
        ORDER BY j.nombre
    ''', (entrenamiento_id,)).fetchall()

    conn.close()
    return render_template('asistencias_entrenamiento.html',
                           entrenamiento=entrenamiento,
                           asistencias=asistencias)

from utils.leer_excel import (
    buscar_fixture_equipo,
    buscar_posiciones_equipo,
    buscar_goleadoras_equipo,
    obtener_equipos_disponibles
)

from utils.leer_excel import (
    buscar_fixture_equipo, 
    buscar_posiciones_equipo, 
    buscar_goleadoras_equipo, 
    obtener_equipos_disponibles
)

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

from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '1234':
            session['username'] = request.form['username']
            session['club'] = 'Everton de La Plata'  # Hardcodeado por ahora
            return redirect(url_for('dashboard'))
        else:
            error = 'Usuario o contraseña incorrectos'
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'], club=session['club'])

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/jugadoras')
def jugadoras():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "<h1>Listado de jugadoras (en construcción)</h1>"

@app.route('/entrenamientos')
def entrenamientos():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "<h1>Listado de entrenamientos (en construcción)</h1>"

@app.route('/fixture')
def fixture():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "<h1>Fixture del club (en construcción)</h1>"


if __name__ == '__main__':
    app.run(debug=True)
