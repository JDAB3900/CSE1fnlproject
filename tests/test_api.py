import pytest
from app import app, mysql
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    rv = client.get('/health')
    assert rv.status_code == 200


def test_register_login_and_crud(client):
    data = {'username':'testuser','password':'testpass'}
    rv = client.post('/auth/register', json=data)
    assert rv.status_code in (201,400)  # 400 if already exists

    rv = client.post('/auth/login', json=data)
    assert rv.status_code == 200
    token = rv.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    emp = {'first_name':'Py','last_name':'Test'}
    rv = client.post('/employees', json=emp, headers=headers)
    assert rv.status_code in (201,400)

    rv = client.get('/employees')
    assert rv.status_code == 200

    rv = client.get('/employees?q=Py')
    assert rv.status_code == 200