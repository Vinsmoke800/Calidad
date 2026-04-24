#comportamiento HTTP de la app

def test_index_redirect(client):
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.location

def test_login_get(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_dashboard_sin_login(client):
    response = client.get('/dashboard', follow_redirects=True)
    assert b'Debes iniciar sesi' in response.data

def test_dashboard_con_admin(client):
    with client.session_transaction() as sess:
        sess['user_role'] = 'Administrador'
        sess['user_name'] = 'Test'

    response = client.get('/dashboard')
    assert response.status_code == 200