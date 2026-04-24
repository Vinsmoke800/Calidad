from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from config import DATABASE_CONFIG
import pyodbc

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
                    return redirect(url_for('vista_parqueos'))
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
    if session['user_role'] != 'Administrador':
        return redirect(url_for('vista_parqueos'))

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
    if session['user_role'] != 'Administrador':
        return redirect(url_for('vista_parqueos'))

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
    if session['user_role'] != 'Administrador':
        return redirect(url_for('vista_parqueos'))

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
    if session['user_role'] != 'Administrador':
        return redirect(url_for('vista_parqueos'))

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
    if session['user_role'] != 'Administrador':
        return redirect(url_for('vista_parqueos'))

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
    usuarios = [{'id': u.id_usuario, 'nombre': u.nombre} for u in cursor.fetchall()]

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
# 👤 VISTA PARQUEOS (USUARIO COMÚN)
# -------------------------------
@app.route('/mi-parqueo')
def vista_parqueos():
    if 'user_role' not in session:
        flash('Debes iniciar sesión.', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        flash("No se pudo conectar a la base de datos.", "danger")
        return redirect(url_for('login'))

    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            p.id_parqueo,
            p.nombre,
            e.numero_espacio,
            e.id_vehiculo
        FROM parqueos p
        INNER JOIN espacios e
            ON p.id_parqueo = e.id_parqueo
        ORDER BY p.id_parqueo, e.numero_espacio
    """)

    parqueos_dict = {}
    for fila in cursor.fetchall():
        pid = fila.id_parqueo
        if pid not in parqueos_dict:
            parqueos_dict[pid] = {"nombre": fila.nombre, "espacios": []}
        parqueos_dict[pid]["espacios"].append({
            "numero_espacio": fila.numero_espacio,
            "ocupado": fila.id_vehiculo is not None
        })

    cursor.close()
    conn.close()

    parqueos = list(parqueos_dict.values())
    return render_template('vista_usuario.html', parqueos=parqueos)

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
                INSERT INTO vehiculos (numero_placa, marca, tipo, color, id_usuario)
                VALUES (?, ?, ?, ?, ?)
            """, (
                request.form['placa'].upper(),
                request.form['marca'],
                request.form['tipo'],
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
# ✏️ EDITAR USUARIO
# -------------------------------
@app.route('/admin/editar-usuario/<int:id_usuario>', methods=['GET', 'POST'])
def editar_usuario(id_usuario):
    if 'user_role' not in session or session['user_role'] != 'Administrador':
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn is None:
        flash("No se pudo conectar a la base de datos.", "danger")
        return redirect(url_for('lista_usuarios'))
    cursor = conn.cursor()
    if request.method == 'POST':
        try:
            cursor.execute("""
                UPDATE usuarios
                SET nombre=?, correo_electronico=?, fecha_nacimiento=?,
                    identificacion=?, numero_carne=?, rol=?
                WHERE id_usuario=?
            """, (
                request.form['nombre'], request.form['correo'],
                request.form['fecha_nacimiento'], request.form['identificacion'],
                request.form['numero_carne'], request.form['rol'], id_usuario
            ))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Usuario actualizado correctamente.", "success")
            return redirect(url_for('lista_usuarios'))
        except Exception as e:
            flash(f"Error al actualizar: {e}", "danger")
    cursor.execute("""
        SELECT id_usuario, nombre, correo_electronico, fecha_nacimiento,
               identificacion, numero_carne, rol
        FROM usuarios WHERE id_usuario=?
    """, (id_usuario,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for('lista_usuarios'))
    return render_template('editar_usuario.html', usuario=usuario)


# -------------------------------
# 🗑️ ELIMINAR USUARIO
# -------------------------------
@app.route('/admin/eliminar-usuario/<int:id_usuario>', methods=['POST'])
def eliminar_usuario(id_usuario):
    if 'user_role' not in session or session['user_role'] != 'Administrador':
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn is None:
        flash("No se pudo conectar.", "danger")
        return redirect(url_for('lista_usuarios'))
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE espacios SET id_vehiculo=NULL
            WHERE id_vehiculo IN (SELECT id_vehiculo FROM vehiculos WHERE id_usuario=?)
        """, (id_usuario,))
        cursor.execute("DELETE FROM vehiculos WHERE id_usuario=?", (id_usuario,))
        cursor.execute("DELETE FROM usuarios WHERE id_usuario=?", (id_usuario,))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Usuario eliminado correctamente.", "success")
    except Exception as e:
        flash(f"Error al eliminar: {e}", "danger")
    return redirect(url_for('lista_usuarios'))


# -------------------------------
# 🚗 GESTIÓN DE VEHÍCULOS
# -------------------------------
@app.route('/admin/vehiculos')
def lista_vehiculos_admin():
    if 'user_role' not in session or session['user_role'] != 'Administrador':
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn is None:
        flash("No se pudo conectar.", "danger")
        return redirect(url_for('dashboard'))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.id_vehiculo, v.numero_placa, v.marca, v.tipo, v.color,
               u.nombre AS nombre_usuario
        FROM vehiculos v
        INNER JOIN usuarios u ON v.id_usuario=u.id_usuario
        ORDER BY v.id_vehiculo
    """)
    vehiculos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('lista_vehiculos_admin.html', vehiculos=vehiculos)


# -------------------------------
# ✏️ EDITAR VEHÍCULO
# -------------------------------
@app.route('/admin/editar-vehiculo/<int:id_vehiculo>', methods=['GET', 'POST'])
def editar_vehiculo(id_vehiculo):
    if 'user_role' not in session or session['user_role'] != 'Administrador':
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn is None:
        flash("No se pudo conectar.", "danger")
        return redirect(url_for('lista_vehiculos_admin'))
    cursor = conn.cursor()
    if request.method == 'POST':
        try:
            cursor.execute("""
                UPDATE vehiculos
                SET numero_placa=?, marca=?, tipo=?, color=?
                WHERE id_vehiculo=?
            """, (
                request.form['numero_placa'].upper(),
                request.form['marca'], request.form['tipo'],
                request.form['color'], id_vehiculo
            ))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Vehículo actualizado correctamente.", "success")
            return redirect(url_for('lista_vehiculos_admin'))
        except Exception as e:
            flash(f"Error al actualizar: {e}", "danger")
    cursor.execute("""
        SELECT v.id_vehiculo, v.numero_placa, v.marca, v.tipo, v.color,
               u.nombre AS nombre_usuario
        FROM vehiculos v
        INNER JOIN usuarios u ON v.id_usuario=u.id_usuario
        WHERE v.id_vehiculo=?
    """, (id_vehiculo,))
    vehiculo = cursor.fetchone()
    cursor.close()
    conn.close()
    if not vehiculo:
        flash("Vehículo no encontrado.", "danger")
        return redirect(url_for('lista_vehiculos_admin'))
    return render_template('editar_vehiculo.html', vehiculo=vehiculo)


# -------------------------------
# 🗑️ ELIMINAR VEHÍCULO
# -------------------------------
@app.route('/admin/eliminar-vehiculo/<int:id_vehiculo>', methods=['POST'])
def eliminar_vehiculo(id_vehiculo):
    if 'user_role' not in session or session['user_role'] != 'Administrador':
        return redirect(url_for('login'))
    conn = get_db_connection()
    if conn is None:
        flash("No se pudo conectar.", "danger")
        return redirect(url_for('lista_vehiculos_admin'))
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE espacios SET id_vehiculo=NULL WHERE id_vehiculo=?", (id_vehiculo,))
        cursor.execute("DELETE FROM vehiculos WHERE id_vehiculo=?", (id_vehiculo,))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Vehículo eliminado correctamente.", "success")
    except Exception as e:
        flash(f"Error al eliminar: {e}", "danger")
    return redirect(url_for('lista_vehiculos_admin'))


# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)