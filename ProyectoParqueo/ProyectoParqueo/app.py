from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from config import DATABASE_CONFIG
import pyodbc
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'


# -------------------------------
# 🔌 CONEXIÓN
# -------------------------------
def get_db_connection():
    try:
        return pyodbc.connect(DATABASE_CONFIG['connection_string'])
    except Exception as e:
        print("Error de conexión:", e)
        return None


# -------------------------------
# 🏠 INICIO
# -------------------------------
@app.route('/')
def index():
    return redirect(url_for('login'))


# -------------------------------
# 🔐 LOGIN
# -------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        clave = request.form['password']

        try:
            conn = get_db_connection()

            if conn is None:
                flash("No se pudo conectar a la base de datos.", "danger")
                return render_template("login.html")

            cursor = conn.cursor()

            cursor.execute("""
                SELECT id_usuario, nombre, rol, clave
                FROM usuarios
                WHERE correo_electronico = ?
            """, (correo,))

            user = cursor.fetchone()

            if user and user.clave == clave:
                session['user_id'] = user.id_usuario
                session['user_name'] = user.nombre
                session['user_role'] = user.rol
                if user.rol == 'Administrador':
                    return redirect(url_for('dashboard'))
                else:
                    return redirect(url_for('parqueos'))
            else:
                flash("Correo o contraseña incorrectos.", "danger")

            cursor.close()
            conn.close()

        except Exception as e:
            flash(f"Error en login: {e}", "danger")

    return render_template("login.html")


# -------------------------------
# 🧭 DASHBOARD
# -------------------------------
@app.route('/dashboard')
def dashboard():
    if 'user_role' not in session:
        flash("Debes iniciar sesión.", "danger")
        return redirect(url_for('login'))

    return render_template(
        "dashboard.html",
        user_name=session['user_name']
    )


# -------------------------------
# 👤 REGISTRAR USUARIO
# -------------------------------
@app.route('/admin/register', methods=['GET', 'POST'])
def register_user():
    if 'user_role' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            conn = get_db_connection()

            if conn is None:
                flash("No se pudo conectar a la base de datos.", "danger")
                return render_template("register_user.html")

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO usuarios
                (
                    nombre,
                    correo_electronico,
                    fecha_nacimiento,
                    identificacion,
                    numero_carne,
                    rol
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                request.form['nombre'],
                request.form['correo'],
                request.form['fecha_nacimiento'],
                request.form['identificacion'],
                request.form['numero_carne'],
                request.form['rol']
            ))

            conn.commit()

            cursor.close()
            conn.close()

            flash("Usuario registrado correctamente.", "success")
            return redirect(url_for('dashboard'))

        except Exception as e:
            flash(f"Error: {e}", "danger")

    return render_template("register_user.html")


# -------------------------------
# 🚗 LISTA DE VEHÍCULOS / PARQUEOS
# -------------------------------
@app.route('/lista_vehiculos')
def lista_vehiculos():
    if 'user_role' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    if conn is None:
        flash("No se pudo conectar a la base de datos.", "danger")
        return redirect(url_for('dashboard'))

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            p.id_parqueo,
            p.nombre,
            e.id_espacio,
            e.numero_espacio,
            e.id_vehiculo
        FROM parqueos p
        INNER JOIN espacios e
            ON p.id_parqueo = e.id_parqueo
        ORDER BY p.id_parqueo, e.numero_espacio
    """)

    datos = cursor.fetchall()

    parqueos_dict = {}

    for fila in datos:
        id_parqueo = fila.id_parqueo

        if id_parqueo not in parqueos_dict:
            parqueos_dict[id_parqueo] = {
                "id_parqueo": fila.id_parqueo,
                "nombre": fila.nombre,
                "espacios": []
            }

        parqueos_dict[id_parqueo]["espacios"].append({
            "id_espacio": fila.id_espacio,
            "numero_espacio": fila.numero_espacio,
            "id_vehiculo": fila.id_vehiculo
        })

    cursor.close()
    conn.close()

    parqueos = list(parqueos_dict.values())

    return render_template(
        "lista_vehiculos.html",
        parqueos=parqueos
    )

# -------------------------------
# 🚗 Detalle VEHÍCULOS / PARQUEOS
# -------------------------------

@app.route('/detalle_vehiculo/<int:id_espacio>', methods=['GET', 'POST'])
def detalle_vehiculo(id_espacio):
    if 'user_role' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Si presiona liberar
    if request.method == 'POST':
        try:
            cursor.execute("""
                UPDATE espacios
                SET id_vehiculo = NULL
                WHERE id_espacio = ?
            """, (id_espacio,))

            conn.commit()
            flash('Espacio liberado correctamente.', 'success')
            return redirect(url_for('lista_vehiculos'))

        except Exception as e:
            conn.rollback()
            flash(f'Error al liberar espacio: {e}', 'danger')

    # Obtener información completa
    cursor.execute("""
        SELECT
            e.id_espacio,
            e.numero_espacio,
            p.nombre AS nombre_parqueo,
            v.id_vehiculo,
            v.marca,
            v.color,
            v.numero_placa,
            v.tipo,
            u.nombre AS nombre_usuario,
            u.identificacion,
            u.numero_carne,
            u.correo_electronico
        FROM espacios e
        INNER JOIN parqueos p
            ON e.id_parqueo = p.id_parqueo
        INNER JOIN vehiculos v
            ON e.id_vehiculo = v.id_vehiculo
        INNER JOIN usuarios u
            ON v.id_usuario = u.id_usuario
        WHERE e.id_espacio = ?
    """, (id_espacio,))

    detalle = cursor.fetchone()

    cursor.close()
    conn.close()

    if not detalle:
        flash('Ese espacio no tiene vehículo asignado.', 'danger')
        return redirect(url_for('lista_vehiculos'))

    return render_template(
        'detalle_vehiculo.html',
        detalle=detalle
    )


# -------------------------------
# 🚗 ASIGNAR VEHÍCULO A ESPACIO
# -------------------------------
@app.route('/asignar_vehiculo', methods=['GET', 'POST'])
def asignar_vehiculo():
    if 'user_role' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    if conn is None:
        flash("No se pudo conectar a la base de datos.", "danger")
        return redirect(url_for('dashboard'))

    cursor = conn.cursor()

    # usuarios
    cursor.execute("""
        SELECT
            id_usuario,
            nombre
        FROM usuarios
        ORDER BY nombre
    """)
    usuarios = cursor.fetchall()

    # parqueos
    cursor.execute("""
        SELECT
            id_parqueo,
            nombre
        FROM parqueos
        ORDER BY nombre
    """)
    parqueos = cursor.fetchall()

    # espacios disponibles
    cursor.execute("""
        SELECT
            id_espacio,
            numero_espacio,
            id_parqueo
        FROM espacios
        WHERE id_vehiculo IS NULL
        ORDER BY id_parqueo, numero_espacio
    """)
    espacios_disponibles = cursor.fetchall()

    if request.method == 'POST':
        try:
            id_usuario = request.form['id_usuario']
            id_parqueo = request.form['id_parqueo']
            id_espacio = request.form['id_espacio']

            # buscar vehículo del usuario
            cursor.execute("""
                SELECT TOP 1
                    id_vehiculo
                FROM vehiculos
                WHERE id_usuario = ?
            """, (id_usuario,))

            vehiculo = cursor.fetchone()

            if not vehiculo:
                flash(
                    "Ese usuario no tiene vehículo registrado.",
                    "danger"
                )
                return redirect(url_for('asignar_vehiculo'))

            id_vehiculo = vehiculo.id_vehiculo

            # actualizar SOLO si:
            # - pertenece al parqueo elegido
            # - sigue disponible
            cursor.execute("""
                UPDATE espacios
                SET id_vehiculo = ?
                WHERE id_espacio = ?
                  AND id_parqueo = ?
                  AND id_vehiculo IS NULL
            """, (
                id_vehiculo,
                id_espacio,
                id_parqueo
            ))

            if cursor.rowcount == 0:
                conn.rollback()

                flash(
                    "No se pudo asignar el vehículo. "
                    "El espacio ya está ocupado o "
                    "no pertenece a ese parqueo.",
                    "danger"
                )

                return redirect(url_for('asignar_vehiculo'))

            conn.commit()

            cursor.close()
            conn.close()

            flash(
                "Vehículo asignado correctamente.",
                "success"
            )

            return redirect(url_for('lista_vehiculos'))

        except Exception as e:
            conn.rollback()

            flash(f"Error: {e}", "danger")
            return redirect(url_for('asignar_vehiculo'))

    cursor.close()
    conn.close()

    return render_template(
        "asignar_vehiculo.html",
        usuarios=usuarios,
        parqueos=parqueos,
        espacios_disponibles=espacios_disponibles
    )


# -------------------------------
# 👥 LISTA DE USUARIOS
# -------------------------------
@app.route('/usuarios')
def lista_usuarios():
    if (
        'user_role' not in session
        or session['user_role'] != 'Administrador'
    ):
        flash("Acceso denegado.", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()

    if conn is None:
        flash("No se pudo conectar a la base de datos.", "danger")
        return redirect(url_for('dashboard'))

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id_usuario,
            nombre,
            correo_electronico,
            identificacion,
            numero_carne,
            rol
        FROM usuarios
    """)

    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "lista_usuarios.html",
        usuarios=usuarios
    )


# -------------------------------
# 🚪 LOGOUT
# -------------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada.", "success")
    return redirect(url_for('login'))


# -------------------------------
# 🅿️ PARQUEOS
# -------------------------------
@app.route('/parqueos')
def parqueos():
    if 'user_role' not in session:
        flash('Debes iniciar sesión.', 'danger')
        return redirect(url_for('login'))

    total = 120
    random.seed(7)
    espacios = [{'numero': i + 1, 'ocupado': random.random() < 0.38} for i in range(total)]
    ocupados = sum(1 for e in espacios if e['ocupado'])
    disponibles = total - ocupados

    return render_template('parqueos.html',
                           total=total,
                           ocupados=ocupados,
                           disponibles=disponibles,
                           espacios=espacios)

# -------------------------------
# 🚗 AGREGAR VEHÍCULO
# -------------------------------
@app.route('/admin/agregar-vehiculo', methods=['GET', 'POST'])
def agregar_vehiculo():
    if 'user_role' not in session or session['user_role'] != 'Administrador':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    usuarios = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, nombre FROM usuarios ORDER BY nombre")
        usuarios = [{'id': u.id_usuario, 'nombre': u.nombre} for u in cursor.fetchall()]
        conn.close()

    if request.method == 'POST':
        try:
            conn = get_db_connection()
            if conn is None:
                flash("No se pudo conectar a la base de datos.", 'danger')
                return render_template('agregar_vehiculo.html', usuarios=usuarios)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO vehiculos (placa, marca, modelo, color, id_usuario)
                VALUES (?, ?, ?, ?, ?)
            """, (
                request.form['placa'].upper(),
                request.form['marca'],
                request.form['modelo'],
                request.form['color'],
                request.form['id_usuario']
            ))
            conn.commit()
            conn.close()
            flash('Vehículo registrado correctamente.', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f"Error: {e}", 'danger')

    return render_template('agregar_vehiculo.html', usuarios=usuarios)

# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)