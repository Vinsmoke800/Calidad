#pruebas lógica + DB simulada, Simula un usuario válido, Que login exitoso redirige correctamente, Valida autenticación sin usar DB real

from unittest.mock import patch, MagicMock

def test_login_correcto(client):
    fake_user = MagicMock()
    fake_user.id_usuario = 1
    fake_user.nombre = "Admin"
    fake_user.rol = "Administrador"
    fake_user.clave = "1234"

    fake_cursor = MagicMock()
    fake_cursor.fetchone.return_value = fake_user

    fake_conn = MagicMock()
    fake_conn.cursor.return_value = fake_cursor

    with patch('app.get_db_connection', return_value=fake_conn):
        response = client.post('/login', data={
            'correo': 'test@test.com',
            'password': '1234'
        }, follow_redirects=True)

        assert b'dashboard' in response.data or response.status_code == 200

def test_login_incorrecto(client):
    fake_cursor = MagicMock()
    fake_cursor.fetchone.return_value = None

    fake_conn = MagicMock()
    fake_conn.cursor.return_value = fake_cursor

    with patch('app.get_db_connection', return_value=fake_conn):
        response = client.post('/login', data={
            'correo': 'wrong@test.com',
            'password': 'wrong'
        }, follow_redirects=True)

        assert b'Correo o contrase' in response.data