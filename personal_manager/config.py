"""Flask configuration."""
import os
from dateutil import tz

class Config:
	"""Base config."""
	STATIC_FOLDER = 'static'
	TEMPLATES_FOLDER = 'templates'
	UTC_TZ  = tz.tzutc()
	LOCAL_TZ = tz.tzlocal()
	DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

	# mail settings
	MAIL_SERVER = os.environ.get('EMAIL_HOST')
	MAIL_PORT = os.environ.get('EMAIL_PORT')
	MAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
	MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
	MAIL_USE_TLS = True
	PER_PAGE_PARAMETER = 10
	BABEL_DEFAULT_LOCALE = 'en'

	# translations
	BABEL_TRANSLATION_DIRECTORIES = os.getcwd() + '/translations'

	# security settings
	SESSION_COOKIE_HTTPONLY = True
	SESSION_COOKIE_SAMESITE = 'Lax'


class ProdConfig(Config):
	SECRET_KEY = os.environ.get('SECRET_KEY')
	EMAIL_CONFIRM_SALT = os.environ.get('EMAIL_CONFIRM_SALT')
	SESSION_COOKIE_SECURE = True
	FLASK_ENV = 'production'
	DEBUG = False
	TESTING = False
	SQLALCHEMY_DATABASE_URI = os.environ.get('PRODUCTION_DATABASE_URI')


class DevConfig(Config):
	SECRET_KEY = 'dev'
	FLASK_ENV = 'development'
	EMAIL_CONFIRM_SALT = 'dev_salt'
	DEBUG = True
	TESTING = False
	SQLALCHEMY_ECHO = True
	SQLALCHEMY_RECORD_QUERIES = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEVELOPMENT_DATABASE_URI')

class TestConfig(Config):
	SECRET_KEY = 'dev'
	FLASK_ENV = 'testing'
	EMAIL_CONFIRM_SALT = 'dev_salt'
	DEBUG = False
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TESTING_DATABASE_URI')
	WTF_CSRF_ENABLED = False
