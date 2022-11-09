"""Flask configuration."""
import os
from dateutil import tz

class Config:
    """Base config."""
    SECRET_KEY = os.getenv('SECRET_KEY')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    UTC_TZ  = tz.tzutc()
    LOCAL_TZ = tz.tzlocal()
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    
    # mail settings
    MAIL_SERVER = os.getenv('EMAIL_HOST')
    MAIL_PORT = os.getenv('EMAIL_PORT')
    MAIL_USERNAME = os.getenv('EMAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = 'confirmation@personal_manager.com'
    MAIL_USE_TLS = True
    EMAIL_CONFIRM_SALT = 'dev_salt'
    PER_PAGE_PARAMETER = 10
    BABEL_DEFAULT_LOCALE = 'en'

    BABEL_TRANSLATION_DIRECTORIES = os.getcwd() + '/translations'


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('PRODUCTION_DATABASE_URI')


class DevConfig(Config):
    SECRET_KEY = 'dev'
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql://dev_user:D3v_user@localhost:3306/personal_manager"
