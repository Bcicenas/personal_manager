import os
from datetime import datetime
from dateutil import tz
from flask import Flask, request, current_app, session, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel

db = SQLAlchemy()
mail = Mail()
csrf = CSRFProtect()
babel = Babel()

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY='dev',
	)
	app.config['UTC-TZ']  = tz.tzutc()
	app.config['LOCAL-TZ'] = tz.tzlocal()
	app.config['DATE-FORMAT'] = "%Y-%m-%d %H:%M:%S"
	app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://dev_user:D3v_user@localhost:3306/personal_manager"
	
	# mail settings
	app.config['MAIL_SERVER'] = os.getenv('EMAIL_HOST')
	app.config['MAIL_PORT'] = os.getenv('EMAIL_PORT')
	app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USERNAME')
	app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
	app.config['MAIL_DEFAULT_SENDER'] = 'confirmation@personal_manager.com'
	app.config['MAIL_USE_TLS'] = True
	app.config['EMAIL_CONFIRM_SALT'] = 'dev_salt'
	app.config['PER_PAGE_PARAMETER'] = 10
	app.config['BABEL_DEFAULT_LOCALE'] = 'en'

	app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.getcwd() + '/translations'

	if test_config is None:
		# load the instance config, if it exists, when not testing
		app.config.from_pyfile('config.py', silent=True)
	else:
		# load the test config if passed in
		app.config.from_mapping(test_config)

	db.init_app(app)
	mail.init_app(app)
	csrf.init_app(app)
	babel.init_app(app)

	# ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	from . import auth
	app.register_blueprint(auth.bp)

	from . import dashboard
	app.register_blueprint(dashboard.bp)
	
	from . import shopping_list
	app.register_blueprint(shopping_list.bp)

	from . import task
	app.register_blueprint(task.bp)	

	from . import user
	app.register_blueprint(user.bp)

	from . import models
	with app.app_context():
		db.create_all()

	app.add_url_rule('/', endpoint='index')
	
	return app

@babel.localeselector
def get_locale():
	if 'locale' in session.keys():
		return session['locale']
	else:
		return current_app.config['BABEL_DEFAULT_LOCALE']
