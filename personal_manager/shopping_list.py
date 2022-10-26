from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from datetime import datetime
from werkzeug.exceptions import abort

from personal_manager.auth import login_required
from .models import User, ShoppingList, ShoppingItem
from . import db
from .forms import ShoppingListForm, ShoppingItemForm, process_form_errors
from sqlalchemy.exc import IntegrityError
import logging

bp = Blueprint('shopping_list', __name__, url_prefix='/shopping_lists')

@bp.route('/list')
@login_required
def list():
	shopping_lists = db.session.execute(
		db.select(ShoppingList).filter_by(user_id=g.user.id).order_by(ShoppingList.created_at.desc())
	).fetchall()
	return render_template('shopping_list/list.html', shopping_lists=shopping_lists)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
	shopping_list = ShoppingList()
	form = ShoppingListForm(request.form, obj=shopping_list)
	error = None
	if request.method == 'POST' and form.validate():
		try:
			form.populate_obj(shopping_list)
			shopping_list.user_id = g.user.id
			db.session.add(shopping_list)
			db.session.commit()	
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = f"Shopping List was not created. Database Error"
		else:
			flash('Shopping List was successfully created', 'success')
			return redirect(url_for('shopping_list.list'))

	if form.errors:	
		error = process_form_errors(form.errors)

	if error is not None:
		flash(error, 'danger')

	return render_template('shopping_list/create.html', form=form)

def get_shopping_id(id, check_owner=True):
	shopping_list = db.session.execute(db.select(ShoppingList).filter_by(id=id)).first()
	if shopping_list is None:
		abort(404, f"Shopping_list id {id} doesn't exist.")

	if check_owner and shopping_list[0].user_id != g.user.id:
		abort(403)

	return shopping_list[0]

@bp.route('/update/<int:id>', methods=('GET', 'POST'))
@login_required
def update(id):
	shopping_list = get_shopping_id(id)
	form = ShoppingListForm(request.form, obj=shopping_list)
	if request.method == 'POST' and form.validate():
		try:
			form.populate_obj(shopping_list)
			shopping_list.last_updated_at = datetime.utcnow()
			db.session.commit()	
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = f"Shopping List was not updated. Database Error"
		else:
			flash('Shopping List was successfully updated', 'success')
			return redirect(url_for('shopping_list.list'))

	if form.errors:	
		error = process_form_errors(form.errors)

	if error is not None:
		flash(error, 'danger')

	return render_template('shopping_list/update.html', shopping_list=shopping_list)

@bp.route('/delete/<int:id>', methods=('POST',))
@login_required
def delete(id):
	shopping_list = get_shopping_id(id)
	if request.method == 'POST':
		error = None
		try:
			db.session.delete(shopping_list)
			db.session.commit()
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = f"Shopping List was not deleted. Database Error"
			current_app.logger.warning(e)
		else:
			flash('Shopping List was successfully deleted', 'success')

		if error is not None:
			flash(error, 'danger')

	
	return redirect(url_for('shopping_list.list'))

@bp.route('/shopping_items/<int:id>')
@login_required
def shopping_items(id):
	shopping_item = ShoppingItem()
	form = ShoppingItemForm(request.form, obj=shopping_item)	
	shopping_list = get_shopping_id(id)
	return render_template('shopping_list/shopping_items.html', form=form, shopping_list=shopping_list, shopping_items=shopping_list.shopping_items)

@bp.route('/create_shopping_list_item/<int:id>', methods=('POST',))
@login_required
def create_shopping_list_item(id):
	get_shopping_id(id)
	shopping_item = ShoppingItem()
	form = ShoppingItemForm(request.form, obj=shopping_item)
	if request.method == 'POST' and form.validate():
		error = None
		try:
			form.populate_obj(shopping_item)
			shopping_item.shopping_list_id=id
			db.session.add(shopping_item)
			db.session.commit()		
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = f"Shopping Item was not created. Database Error"
		else:
			flash('Shopping Item was successfully created', 'success')

	if form.errors:	
		error = process_form_errors(form.errors)

	if error is not None:
		flash(error, 'danger')

	return redirect(url_for('shopping_list.shopping_items', id=id))

@bp.route('/delete_shopping_list_item/<int:id>', methods=('POST',))
@login_required
def delete_shopping_list_item(id):
	shopping_item = get_shopping_item_id(id)
	if request.method == 'POST':
		try:
			db.session.delete(shopping_item)
			db.session.commit()	
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = f"Shopping Item was not deleted. Database Error"
		else:
			flash('Shopping Item was successfully deleted', 'success')

		if error is not None:
			flash(error, 'danger')
	
	return redirect(url_for('shopping_list.shopping_items', id=request.form['shopping_list_id']))

def get_shopping_item_id(id, check_owner=True):
	shopping_item = db.session.execute(db.select(ShoppingItem).filter_by(id=id)).first()
	if shopping_item is None:
		abort(404, f"Shopping_item id {id} doesn't exist.")

	if check_owner and shopping_item[0].shopping_list.user_id != g.user.id:
		abort(403)

	return shopping_item[0]