import functools

from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from . import db
from .models import User

from werkzeug.security import check_password_hash
from sqlalchemy.exc import IntegrityError
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import or_

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
			error = f"Username or Email already exists"
		else:
			flash('User successfully registered', 'success')
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
			error = 'Incorrect username.'
		elif not user[0].email_confirmed:
			error = 'Email is not confirmed'
		elif not check_password_hash(user[0].password, password):
			error = 'Incorrect password.'

		if error is None:
			session.clear()
			session['user_id'] = user[0].id
			flash('Login successfully', 'success')
			return redirect(url_for('index'))

		flash(error, 'danger')

	return render_template('auth/login.html')

@bp.route('/confirm/<token>')
def confirm_email(token):
	print(token)
	ts = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
	try:
		email = ts.loads(token, salt=current_app.config['EMAIL_CONFIRM_SALT'], max_age=86400)
	except:
		abort(404)

	user = User.query.filter_by(email=email).first_or_404()

	user.email_confirmed = True

	db.session.commit()
	flash('Email was confirmed successfully', 'success')
	return redirect(url_for("auth.login"))
	
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
			flash('Access denied', 'danger')
			return redirect(url_for('auth.login'))
		return view(**kwargs)

	return wrapped_view

