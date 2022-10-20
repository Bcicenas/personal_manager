from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort

from personal_manager.auth import login_required

bp = Blueprint('shopping_list', __name__, url_prefix='/shopping_lists')

@bp.route('/list')
@login_required
def list():
	db = current_app.mysql.connection.cursor()
	db.execute(
		'''SELECT p.id, name, created_at, last_updated_at
		FROM shopping_list p JOIN user u ON p.owner_id = u.id
		WHERE u.id = %s
		ORDER BY created_at DESC''',
		(g.user['id'],)
	)
	shopping_lists = db.fetchall()
	return render_template('shopping_list/list.html', shopping_lists=shopping_lists)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
	if request.method == 'POST':
		name = request.form['name']
		error = None

		if not name:
			error = 'Name is required.'

		if error is not None:
			flash(error, 'danger')
		else:
			db_conn = current_app.mysql.connection
			db = db_conn.cursor()
			db.execute(
				'''INSERT INTO shopping_list (name, owner_id)
				VALUES ( %s, %s)''',
				(name, g.user['id'])
			)
			db_conn.commit()
			db.close()
			flash('Shopping List was successfully created', 'success')
			return redirect(url_for('shopping_list.list'))

	return render_template('shopping_list/create.html')

def get_shopping_id(id, check_owner=True):
	db = current_app.mysql.connection.cursor()
	db.execute(
		'''SELECT p.id, name, created_at, last_updated_at, owner_id
		 FROM shopping_list p JOIN user u ON p.owner_id = u.id
		 WHERE p.id = %s''',
		(id,)
	)
	shopping_list = db.fetchone()
	if shopping_list is None:
		abort(404, f"Shopping_list id {id} doesn't exist.")

	if check_owner and shopping_list['owner_id'] != g.user['id']:
		abort(403)

	return shopping_list

@bp.route('/update/<int:id>', methods=('GET', 'POST'))
@login_required
def update(id):
	shopping_list = get_shopping_id(id)

	if request.method == 'POST':
		name = request.form['name']
		error = None

		if not name:
			error = 'Name is required.'

		if error is not None:
			flash(error, 'danger')
		else:
			db_conn = current_app.mysql.connection
			db = db_conn.cursor()
			db.execute(
				'''UPDATE shopping_list SET name = %s
				 WHERE id = %s''',
				(name, id)
			)
			db_conn.commit()
			db.close()
			flash('Shopping List was successfully updated', 'success')
			return redirect(url_for('shopping_list.list'))

	return render_template('shopping_list/update.html', shopping_list=shopping_list)

@bp.route('/delete/<int:id>', methods=('POST',))
@login_required
def delete(id):
	get_shopping_id(id)
	db_conn = current_app.mysql.connection
	db = db_conn.cursor()
	db.execute('''DELETE FROM shopping_list WHERE id = %s''', (id,))
	db_conn.commit()
	db.close()
	flash('Shopping List was successfully deleted', 'success')
	return redirect(url_for('shopping_list.list'))

@bp.route('/shopping_items/<int:id>')
@login_required
def shopping_items(id):
	shopping_list = get_shopping_id(id)
	db = current_app.mysql.connection.cursor()
	db.execute(
		'''SELECT si.id, si.name
		 FROM shopping_item si JOIN shopping_list sl ON si.shopping_list_id = sl.id
		 WHERE sl.id = %s
		 ORDER BY si.created_at DESC''',
		(id, )
	)
	shopping_items = db.fetchall()
	return render_template('shopping_list/shopping_items.html', shopping_items=shopping_items, shopping_list=shopping_list)

@bp.route('/create_shopping_list_item/<int:id>', methods=('POST',))
@login_required
def create_shopping_list_item(id):
	get_shopping_id(id)
	if request.method == 'POST':
		name = request.form['name']
		error = None

		if not name:
			error = 'Name is required.'

		if error is not None:
			flash(error, 'danger')
		else:
			db_conn = current_app.mysql.connection
			db = db_conn.cursor()
			db.execute(
				'''INSERT INTO shopping_item (name, shopping_list_id)
				VALUES ( %s, %s)''',
				(name, id)
			)
			db_conn.commit()
			db.close()
			flash('Shopping Item was successfully created', 'success')

	return redirect(url_for('shopping_list.shopping_items', id=id))

@bp.route('/delete_shopping_list_item/<int:id>', methods=('POST',))
@login_required
def delete_shopping_list_item(id):
	get_shopping_item_id(id)
	db_conn = current_app.mysql.connection
	db = db_conn.cursor()
	db.execute('''DELETE FROM shopping_item WHERE id = %s''', (id,))
	db_conn.commit()
	db.close()
	flash('Shopping Item was successfully deleted', 'success')
	return redirect(url_for('shopping_list.shopping_items', id=request.form['shopping_list_id']))

def get_shopping_item_id(id, check_owner=True):
	db = current_app.mysql.connection.cursor()
	db.execute(
		'''SELECT si.id, sl.owner_id
		 FROM shopping_item si 
		 JOIN shopping_list sl ON sl.id = si.shopping_list_id
		 JOIN user u ON u.id = sl.owner_id
		 WHERE si.id = %s''',
		(id,)
	)
	shopping_list = db.fetchone()
	if shopping_list is None:
		abort(404, f"Shopping_item id {id} doesn't exist.")

	if check_owner and shopping_list['owner_id'] != g.user['id']:
		abort(403)

	return shopping_list