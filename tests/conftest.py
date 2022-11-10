import os
import tempfile

import pytest
from personal_manager import create_app

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
	_data_sql = f.read().decode('utf8')

from sqlalchemy import create_engine
from sqlalchemy import text

@pytest.fixture
def app():
	db_fd, db_path = tempfile.mkstemp()
	app = create_app('testing')
	
	yield app

	os.close(db_fd)
	os.unlink(db_path)


@pytest.fixture
def client(app):
	return app.test_client()


@pytest.fixture
def runner(app):
	return app.test_cli_runner()

class AuthActions(object):
	def __init__(self, client):
		self._client = client

	def login(self, username='admin', password='A@sdas123_'):
		return self._client.post(
			'/auth/login',
			data={'username': username, 'password': password}
		)

	def logout(self):
		return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
	return AuthActions(client)

@pytest.fixture
def load_db(app):
	with app.app_context():
		
		# load data sql
		engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], echo=True)

		with engine.connect() as con:
			con.execute(_data_sql)
			
	return 'db_loaded'
	