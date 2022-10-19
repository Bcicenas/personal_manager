from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from personal_manager.auth import login_required
from personal_manager.db import get_db

bp = Blueprint('shopping_list', __name__, url_prefix='/shopping_lists')

@bp.route('/list')
@login_required
def list():
	db = get_db()
	shopping_lists = db.execute(
		'SELECT p.id, name, created_at, last_updated_at'
		' FROM shopping_list p JOIN user u ON p.owner_id = u.id'
		' WHERE u.id = ?'
		' ORDER BY created_at DESC',
		(g.user['id'],)
	).fetchall()
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
			db = get_db()
			db.execute(
				'INSERT INTO shopping_list (name, owner_id)'
				' VALUES ( ?, ?)',
				(name, g.user['id'])
			)
			db.commit()
			flash('Shopping List was successfully created', 'success')
			return redirect(url_for('shopping_list.list'))

	return render_template('shopping_list/create.html')

def get_shopping_id(id, check_owner=True):
	shopping_list = get_db().execute(
		'SELECT p.id, name, created_at, last_updated_at, owner_id'
		' FROM shopping_list p JOIN user u ON p.owner_id = u.id'
		' WHERE p.id = ?',
		(id,)
	).fetchone()

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
			db = get_db()
			db.execute(
				'UPDATE shopping_list SET name = ?'
				' WHERE id = ?',
				(name, id)
			)
			db.commit()
			flash('Shopping List was successfully updated', 'success')
			return redirect(url_for('shopping_list.list'))

	return render_template('shopping_list/update.html', shopping_list=shopping_list)

@bp.route('/delete/<int:id>', methods=('POST',))
@login_required
def delete(id):
	get_shopping_id(id)
	db = get_db()
	db.execute('DELETE FROM shopping_list WHERE id = ?', (id,))
	db.commit()
	flash('Shopping List was successfully deleted', 'success')
	return redirect(url_for('shopping_list.list'))

@bp.route('/shopping_items/<int:id>')
@login_required
def shopping_items(id):
	shopping_list = get_shopping_id(id)
	db = get_db()
	shopping_items = db.execute(
		'SELECT si.id, si.name'
		' FROM shopping_item si JOIN shopping_list sl ON si.shopping_list_id = sl.id'
		' WHERE sl.id = ?'
		' ORDER BY si.created_at DESC',
		(id, )
	).fetchall()
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
			db = get_db()
			db.execute(
				'INSERT INTO shopping_item (name, shopping_list_id)'
				' VALUES ( ?, ?)',
				(name, id)
			)
			db.commit()
			flash('Shopping Item was successfully created', 'success')

	return redirect(url_for('shopping_list.shopping_items', id=id))