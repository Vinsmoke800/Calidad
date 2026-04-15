from flask import Flask, render_template, request, redirect, url_for, session, flash
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
@app.route('/')
def index():
    return redirect(url_for('login'))

# -------------------------------
# 🔐 LOGIN (CORREGIDO)
# -------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        clave = request.form['password']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            query = """
                SELECT id_usuario, nombre, rol, clave
                FROM usuarios
                WHERE correo_electronico = ?
            """
            cursor.execute(query, (correo,))
            user = cursor.fetchone()

            if user and user.clave == clave:
                session['user_id'] = user.id_usuario
                session['user_name'] = user.nombre
                session['user_role'] = user.rol

                return redirect(url_for('dashboard'))
            else:
                flash('Correo o contraseña incorrectos.', 'danger')

        except Exception as e:
            flash(f"Error en login: {e}", 'danger')

    return render_template('login.html')

# -------------------------------
# 🧭 DASHBOARD
# -------------------------------
@app.route('/dashboard')
def dashboard():
    if 'user_role' in session:
        return render_template('dashboard.html', user_name=session['user_name'])
    else:
        flash('No tienes permisos.', 'danger')
        return redirect(url_for('login'))

# -------------------------------
# 👤 REGISTRAR USUARIO (CORREGIDO)
# -------------------------------
@app.route('/admin/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO usuarios
                (nombre, correo_electronico, fecha_nacimiento, identificacion, numero_carne, rol)
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
            flash('Usuario registrado correctamente.', 'success')
            return redirect(url_for('dashboard'))

        except Exception as e:
            flash(f"Error: {e}", 'danger')

    return render_template('register_user.html')

# -------------------------------
# 🚪 LOGOUT
# -------------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada.', 'success')
    return redirect(url_for('login'))

# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)