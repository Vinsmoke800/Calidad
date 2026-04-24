#Prueba la base de datos con los usuarios, conexión, y CRUD

from app import get_db_connection

def test_conexion_db():
    conn = get_db_connection()
    assert conn is not None
    conn.close()

def test_insert_usuario():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO usuarios
        (nombre, correo_electronico, fecha_nacimiento, identificacion, numero_carne, rol, clave)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        'Test User',
        'test_user@test.com',
        '2000-01-01',
        '123456',
        'A001',
        'Usuario',
        '1234'
    ))

    conn.commit()

    cursor.execute("SELECT * FROM usuarios WHERE correo_electronico = ?", ('test_user@test.com',))
    user = cursor.fetchone()

    assert user is not None

    # limpieza
    cursor.execute("DELETE FROM usuarios WHERE correo_electronico = ?", ('test_user@test.com',))
    conn.commit()

    conn.close()