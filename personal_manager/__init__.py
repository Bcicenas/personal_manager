import os
from datetime import datetime
from flask import Flask, request, current_app, session, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel, lazy_gettext
from flask import Flask, render_template
from personal_manager.config import DevConfig, ProdConfig, TestConfig
from flask_alembic import Alembic

db = SQLAlchemy()
mail = Mail()
csrf = CSRFProtect()
babel = Babel()
alembic = Alembic()

def page_not_found(e):
	return render_template('404.html', e=e), 404

def create_app(app_env='development'):
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	
	if app_env == 'development':
		app.config.from_object('personal_manager.config.DevConfig')
	elif app_env == 'production':
		app.config.from_object('personal_manager.config.ProdConfig')
	else:
		app.config.from_object('personal_manager.config.TestConfig')	

	# custom error handlers
	app.register_error_handler(404, page_not_found)
	db.init_app(app)
	mail.init_app(app)
	csrf.init_app(app)
	babel.init_app(app, locale_selector=get_locale)
	alembic.init_app(app)

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

	from . import plan
	app.register_blueprint(plan.bp)	

	from . import user
	app.register_blueprint(user.bp)

	from . import models

	from .utils import get_current_year
	# global variables for templates
	app.jinja_env.globals['get_current_year'] = get_current_year()

	with app.app_context():
		db.create_all()

	app.add_url_rule('/', endpoint='index')
	
	return app

def get_locale():
	if 'locale' in session.keys():
		return session['locale']
	else:
		return current_app.config['BABEL_DEFAULT_LOCALE']

# translate pagination
def get_localized_msg(record_name, current_page, total, items_per_page):
	start = (current_page - 1) * items_per_page + 1
	end = total if (start + (items_per_page - 1)) > total else (start + (items_per_page - 1))
	return lazy_gettext('displaying') + " <b>{start} - {end}</b> " + lazy_gettext('in total') + " <b>{total}</b>"

def convert_date_time(datetime_obj, from_tz, to_tz):
	return datetime_obj.replace(tzinfo=current_app.config[from_tz]).astimezone(current_app.config[to_tz]).strftime(current_app.config['DATE_FORMAT'])

def convert_list_tuple_to_list(tuple_list):
	out = []
	for t in tuple_list:
		for item in t:
			out.append(item)

	return out

