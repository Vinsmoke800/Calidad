#pruebas de flujo completo

from unittest.mock import patch, MagicMock

def test_asignar_sin_vehiculo(client):
    with client.session_transaction() as sess:
        sess['user_role'] = 'Administrador'

    fake_cursor = MagicMock()
    fake_cursor.fetchone.return_value = None  # usuario sin vehículo

    fake_conn = MagicMock()
    fake_conn.cursor.return_value = fake_cursor

    with patch('app.get_db_connection', return_value=fake_conn):
        response = client.post('/asignar_vehiculo', data={
            'id_usuario': 1,
            'id_parqueo': 1,
            'id_espacio': 1
        }, follow_redirects=True)

        assert b'no tiene veh' in response.data.lower()