import functools

from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from . import db
from .models import User
from .forms import EmailForm, PasswordForm, process_form_errors
from werkzeug.security import check_password_hash
from werkzeug.exceptions import abort
from sqlalchemy.exc import IntegrityError
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import or_
from flask_babel import lazy_gettext

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
	if request.method == 'POST':
		error = None
		try:
			user = User(username=request.form['username'], email=request.form['email'], password=request.form['password'])
			db.session.add(user)
			db.session.commit()
			ts = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
			user.send_email_confirmation(ts)			
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = lazy_gettext('Username or Email already exists')
		else:
			flash(lazy_gettext('User successfully registered'), 'success')
			return redirect(url_for("auth.login"))

		flash(error, 'danger')

	return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		error = None
		user = db.session.execute(db.select(User).filter(or_(User.username == username, User.email == username))).first()

		if user is None:
			error = lazy_gettext('Incorrect username.')
		elif not user[0].email_confirmed:
			error = lazy_gettext('Email is not confirmed')
		elif not check_password_hash(user[0].password, password):
			error = lazy_gettext('Incorrect password.')

		if error is None:
			locale = session['locale'] if session['locale'] else None
			session.clear()
			session['locale'] = locale
			session['user_id'] = user[0].id
			flash(lazy_gettext('Login successfully'), 'success')
			return redirect(url_for('index'))

		flash(error, 'danger')

	return render_template('auth/login.html')

@bp.route('/confirm/<token>')
def confirm_email(token):
	ts = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
	try:
		email = ts.loads(token, salt=current_app.config['EMAIL_CONFIRM_SALT'], max_age=86400)
	except:
		abort(404, 'Token has expired')

	user = User.query.filter_by(email=email).first_or_404()

	user.email_confirmed = True

	db.session.commit()
	flash(lazy_gettext('Email was confirmed successfully'), 'success')
	return redirect(url_for("auth.login"))

@bp.route('/forgot_password', methods=('GET', 'POST'))
def forgot_password():
	form = EmailForm()
	error = None
	if request.method == 'POST' and form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first_or_404()
		if user.email_confirmed:
			ts = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
			user.send_password_reset(ts)
			flash(lazy_gettext('Password reset link was sent to ') + form.email.data, 'success')
			return redirect(url_for("index"))
		else:
			error = lazy_gettext('Email is not confirmed')

		if error:
			flash(error, 'danger')

	return render_template('auth/forgot_password.html', form=form)


@bp.route('/reset_password/<token>', methods=["GET", "POST"])
def reset_password(token):
	ts = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
	try:
		email = ts.loads(token, salt=current_app.config['EMAIL_CONFIRM_SALT'], max_age=86400)
	except:
		abort(404, 'Token has expired')

	error = None
	form = PasswordForm()

	if request.method == 'POST' and form.validate_on_submit():
		user = User.query.filter_by(email=email).first_or_404()

		try:
			user.password = form.password.data
			db.session.commit()
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = lazy_gettext('Password reset failed. Database Error')
		else:
			flash(lazy_gettext('Password was successfully changed'), 'success')
			return redirect(url_for('auth.login'))

	if form.errors:	
		error = process_form_errors(form.errors)

	if error is not None:
		flash(error, 'danger')

	return render_template('auth/reset_password.html', form=form, token=token)

@bp.before_app_request
def load_logged_in_user():
	user_id = session.get('user_id')

	if user_id is None:
		g.user = None
	else:
		g.user = db.session.execute(db.select(User).filter_by(id=user_id)).first()
		if g.user is not None:
			g.user = g.user[0]

@bp.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('index'))

def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			flash(lazy_gettext('Access denied'), 'danger')
			return redirect(url_for('auth.login'))
		return view(**kwargs)

	return wrapped_view
