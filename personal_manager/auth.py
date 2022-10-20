import functools

from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		db_conn = current_app.mysql.connection
		db = db_conn.cursor()
		error = None

		if not username:
			error = 'Username is required.'
		elif not password:
			error = 'Password is required.'

		if error is None:
			try:
				db.execute(
					'''INSERT INTO user (username, password) VALUES (%s, %s)''',
					(username, generate_password_hash(password)),
				)
				db_conn.commit()
				db.close()
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
		db = current_app.mysql.connection.cursor()
		error = None
		db.execute(
			'''SELECT * FROM user WHERE username = %s''', (username,)
		)
		user = db.fetchone()
		db.close()

		if user is None:
			error = 'Incorrect username.'
		elif not check_password_hash(user['password'], password):
			error = 'Incorrect password.'

		if error is None:
			session.clear()
			session['user_id'] = user['id']
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
		db = current_app.mysql.connection.cursor()
		db.execute(
			'''SELECT * FROM user WHERE id = %s''', (user_id,)
		)
		g.user = db.fetchone()
		db.close

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
