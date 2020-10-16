import os

import pytest

from . import create_app
from .models import db, User

from flask_migrate import upgrade


@pytest.fixture
def client():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                                        'test.db')
    app.config['TESTING'] = True

    with app.test_client() as client:
        db.init_app(app)
        app.app_context().push()
        upgrade()
        yield client

    os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.db'))


# Auth
def test_signup(client):
    user = User(username='adsf', password='asdf')
    db.session.add(user)
    db.session.commit()
    signup_res = client.post('/auth/signup', json=dict(username="user1", password="pass"))
    assert signup_res.status_code == 200


def test_login(client):
    client.post('/auth/signup', json=dict(username="user1", password="pass"))

    login_res = client.post('/auth/login', json=dict(username="user1", password="pass"))
    assert login_res.status_code == 200


def test_logout(client):
    client.post('/auth/signup', json=dict(username="user1", password="pass"))

    login_res = client.post('/auth/login', json=dict(username="user1", password="pass"))

    logout_res = client.get('/auth/logout', headers={"Authorization": "Bearer " + login_res.json["access_token"]})
    assert logout_res.status_code == 200


def test_refresh(client):
    client.post('/auth/signup', json=dict(username="user1", password="pass"))

    login_res = client.post('/auth/login', json=dict(username="user1", password="pass"))

    refresh_res = client.post('/auth/refresh', headers={"Authorization": "Bearer " + login_res.json["refresh_token"]})
    assert refresh_res.status_code == 200
