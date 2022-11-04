import pytest
from flask import g, session
from itsdangerous import URLSafeTimedSerializer
import logging

def test_load_db(load_db):
	assert load_db == 'db_loaded'

def test_register(client, app):
	assert client.get('/auth/register').status_code == 200
	response = client.post(
		'/auth/register', data={'username': 'admin2', 'email': 'test@example.com', 'password': '@dMin21_'}
	)
	assert response.headers["Location"] == '/auth/login'
	response = client.get('/auth/login', follow_redirects=True)
	assert b'User successfully registered' in response.data


def test_confirm_email(client, app):
	with app.app_context():
		ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])
		token = ts.dumps('test@example.com', salt=app.config['EMAIL_CONFIRM_SALT'])
		response = client.get('/auth/confirm/' + token, follow_redirects=True)
		assert b'Email was confirmed successfully' in response.data


def test_forgot_password(client, app):
	assert client.get('/auth/forgot_password').status_code == 200
	response = client.post(
		'/auth/forgot_password', data={'email': 'test@example.com'}
	)
	assert response.headers["Location"] == '/'
	response = client.get('/', follow_redirects=True)
	assert b'Password reset link was sent to' in response.data


@pytest.mark.parametrize(('password', 'message'), (
	('', b'Password is required.'),
	('test', b'Please choose a stronger password.'),
))
def test_reset_password_validate_input(client, app, password, message):
	with app.app_context():
		ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])
		token = ts.dumps('test@example.com', salt=app.config['EMAIL_CONFIRM_SALT'])
		response = client.post('/auth/reset_password/' + token, data={'password': password})
		assert message in response.data

def test_reset_password(client, app):
	with app.app_context():
		ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])
		token = ts.dumps('test@example.com', salt=app.config['EMAIL_CONFIRM_SALT'])
		response = client.post('/auth/reset_password/' + token, data={'password': '@dMin21_'})
		print(response.data)
		assert response.headers["Location"] == '/auth/login'
		response = client.get('/auth/login', follow_redirects=True)
		assert b'Password was successfully changed' in response.data

@pytest.mark.parametrize(('username', 'email', 'password', 'message'), (
	('', '', '', b'Username is required.'),
	('a', 'test', '', b'Email is invalid'),
	('a', 'test@email.com', '', b'Password is required.'),
	('a', 'test@email.com', 'a', b'Please choose a stronger password.'),
	('admin', 'test@a.com', 'A@sdas123_', b'Username or Email already exists'),
	('test_user', 'user@email.com', 'A@sdas124_', b'Username or Email already exists'),
))
def test_register_validate_input(client, username, email, password, message):
	response = client.post(
		'/auth/register',
		data={'username': username, 'email': email, 'password': password}
	)
	assert message in response.data

def test_login(client, auth):
	assert client.get('/auth/login').status_code == 200
	response = auth.login()
	assert response.headers["Location"] == "/"

	with client:
		client.get('/')
		assert session['user_id'] == 1
		assert g.user.username == 'admin'

def test_login_with_email(client, auth):
	assert client.get('/auth/login').status_code == 200
	response = auth.login(username="admin@email.com")
	assert response.headers["Location"] == "/"

	with client:
		client.get('/')
		assert session['user_id'] == 1
		assert g.user.username == 'admin'

@pytest.mark.parametrize(('username', 'password', 'message'), (
	('test_user', 'A@sdas124_', b'Email is not confirmed'),
))
def test_login_email_not_confirmed(auth, username, password, message):
	response = auth.login(username, password)
	assert message in response.data

@pytest.mark.parametrize(('username', 'password', 'message'), (
	('admin4', '', b'Incorrect username.'),
	('admin', 'admin4', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
	response = auth.login(username, password)
	assert message in response.data

def test_logout(client, auth):
	auth.login()

	with client:
		auth.logout()
		assert 'user_id' not in session
