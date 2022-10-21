import functools

from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from . import db
from .models import User

from werkzeug.security import check_password_hash, generate_password_hash
from password_strength import PasswordPolicy

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
	if request.method == 'POST':
		username = request.form['username']
		email = request.form['email']
		password = request.form['password']
		error = None

		if not username:
			error = 'Username is required.'
		elif not password:
			error = 'Password is required.'

		policy = PasswordPolicy.from_names(
			length=8,
			uppercase=1,
			numbers=1,
			special=1,
		)

		if error is None and password and policy.test(password):
			error = '''Please choose a stronger password.
				<br>Must contain at least 8 characters
				<br>Must contain at least 1 uppercase letter
				<br>Must contain at least 1 uppercase letter
				<br>Must contain at least 1 number
				<br>Must contain at least 1 special character'''

		if error is None:
			try:
				user = User(username=username,email=email, password=generate_password_hash(password))
				db.session.add(user)
				db.session.commit()				
			except db.IntegrityError:
				error = f"User {username} is already registered."
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
		user = db.session.execute(db.select(User).filter_by(username=username)).first()[0]

		if user is None:
			error = 'Incorrect username.'
		elif not check_password_hash(user.password, password):
			error = 'Incorrect password.'

		if error is None:
			session.clear()
			session['user_id'] = user.id
			flash('Login successfully', 'success')
			return redirect(url_for('index'))

		flash(error, 'danger')

	return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
	user_id = session.get('user_id')

	if user_id is None:
		g.user = None
	else:
		g.user = db.session.execute(db.select(User).filter_by(id=user_id)).first()[0]

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
