from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from datetime import datetime
from werkzeug.exceptions import abort

from personal_manager.auth import login_required
from .models import User, ShoppingList, ShoppingItem
from . import db, get_localized_msg
from .forms import ShoppingListForm, ShoppingItemForm, process_form_errors
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
import logging
from flask_paginate import Pagination, get_page_parameter
from flask_babel import lazy_gettext

bp = Blueprint('shopping_list', __name__, url_prefix='/shopping_lists')

@bp.route('/list', methods=('GET', 'POST'))
@login_required
def list():
	page = request.args.get(get_page_parameter(), type=int, default=1)
	if request.method == 'POST':
		name = request.form['s_name']
		name_pattern = "%{}%".format(name)
		shopping_lists = db.paginate(db.select(ShoppingList).filter(and_(ShoppingList.user_id == g.user.id, ShoppingList.name.like(name_pattern))).order_by(ShoppingList.created_at.desc()), page=page, per_page=current_app.config['PER_PAGE_PARAMETER'])
	else:	
		shopping_lists = db.paginate(db.select(ShoppingList).filter_by(user_id=g.user.id).order_by(ShoppingList.created_at.desc()), page=page, per_page=current_app.config['PER_PAGE_PARAMETER'])
	items_per_page = current_app.config['PER_PAGE_PARAMETER']
	display_msg = get_localized_msg(lazy_gettext('shopping lists'), page, shopping_lists.total, items_per_page)
	pagination = Pagination(page=page, total=shopping_lists.total, per_page=items_per_page, display_msg=display_msg)
	return render_template('shopping_list/list.html', shopping_lists=shopping_lists, pagination=pagination)

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
			error = lazy_gettext('Shopping List was not created. Database Error')
		else:
			flash(lazy_gettext('Shopping List was successfully created'), 'success')
			return redirect(url_for('shopping_list.list'))

	if form.errors:	
		error = process_form_errors(form.errors)

	if error is not None:
		flash(error, 'danger')

	return render_template('shopping_list/create.html', form=form)

def get_shopping_id(id, check_owner=True):
	shopping_list = db.session.execute(db.select(ShoppingList).filter_by(id=id)).first()
	if shopping_list is None:
		abort(404, lazy_gettext('Shopping list id ') + str(id) + lazy_gettext(" doesn't exist."))

	if check_owner and shopping_list[0].user_id != g.user.id:
		abort(403)

	return shopping_list[0]

@bp.route('/update/<int:id>', methods=('GET', 'POST'))
@login_required
def update(id):
	shopping_list = get_shopping_id(id)
	form = ShoppingListForm(request.form, obj=shopping_list)
	error = None
	if request.method == 'POST' and form.validate():
		try:
			form.populate_obj(shopping_list)
			shopping_list.last_updated_at = datetime.utcnow()
			db.session.commit()	
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = lazy_gettext('Shopping List was not updated. Database Error')
		else:
			flash(lazy_gettext('Shopping List was successfully updated'), 'success')
			return redirect(url_for('shopping_list.list'))

	if form.errors:	
		error = process_form_errors(form.errors)

	if error is not None:
		flash(error, 'danger')

	return render_template('shopping_list/update.html', shopping_list=shopping_list, form=form)

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
			error = lazy_gettext('Shopping List was not deleted. Database Error')
			current_app.logger.warning(e)
		else:
			flash(lazy_gettext('Shopping List was successfully deleted'), 'success')

		if error is not None:
			flash(error, 'danger')

	
	return redirect(url_for('shopping_list.list'))

@bp.route('/shopping_items/<int:id>', methods=('GET', 'POST'))
@login_required
def shopping_items(id):
	shopping_item = ShoppingItem()
	form = ShoppingItemForm(request.form, obj=shopping_item)	
	shopping_list = get_shopping_id(id)
	page = request.args.get(get_page_parameter(), type=int, default=1)
	if request.method == 'POST':
		name = request.form['s_name']
		name_pattern = "%{}%".format(name)
		shopping_items = db.paginate(db.select(ShoppingItem).filter(and_(ShoppingItem.shopping_list_id == id, ShoppingItem.name.like(name_pattern))).order_by(ShoppingItem.created_at.desc()), page=page, per_page=current_app.config['PER_PAGE_PARAMETER'])
	else:
		shopping_items = db.paginate(db.select(ShoppingItem).filter_by(shopping_list_id=id).order_by(ShoppingItem.created_at.desc()), page=page, per_page=current_app.config['PER_PAGE_PARAMETER'])
	items_per_page = current_app.config['PER_PAGE_PARAMETER']
	display_msg = get_localized_msg(lazy_gettext('shopping items'), page, shopping_items.total, items_per_page)
	pagination = Pagination(page=page, total=shopping_items.total, per_page=items_per_page, display_msg=display_msg)
	return render_template('shopping_list/shopping_items.html', form=form, shopping_list=shopping_list, shopping_items=shopping_items, pagination=pagination)

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
			error = lazy_gettext('Shopping Item was not created. Database Error')
		else:
			flash(lazy_gettext('Shopping Item was successfully created'), 'success')

	if form.errors:	
		error = process_form_errors(form.errors)

	if error is not None:
		flash(error, 'danger')

	return redirect(url_for('shopping_list.shopping_items', id=id))

@bp.route('/delete_shopping_list_item/<int:id>', methods=('POST',))
@login_required
def delete_shopping_list_item(id):
	shopping_item = get_shopping_item_id(id)
	error = None
	if request.method == 'POST':
		try:
			db.session.delete(shopping_item)
			db.session.commit()	
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = lazy_gettext('Shopping Item was not deleted. Database Error')
		else:
			flash(lazy_gettext('Shopping Item was successfully deleted'), 'success')

		if error is not None:
			flash(error, 'danger')
	
	return redirect(url_for('shopping_list.shopping_items', id=request.form['shopping_list_id']))

def get_shopping_item_id(id, check_owner=True):
	shopping_item = db.session.execute(db.select(ShoppingItem).filter_by(id=id)).first()
	if shopping_item is None:
		abort(404, lazy_gettext('Shopping item id ') + str(id) + lazy_gettext(" doesn't exist."))

	if check_owner and shopping_item[0].shopping_list.user_id != g.user.id:
		abort(403)

	return shopping_item[0]
	