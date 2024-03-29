from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from datetime import datetime
from werkzeug.exceptions import abort
from . import convert_date_time
from personal_manager.auth import login_required
from .models import Task, ShoppingList
from .forms import TaskForm, process_form_errors
from . import db, get_localized_msg
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from flask_paginate import Pagination, get_page_parameter
from flask_babel import lazy_gettext

bp = Blueprint('task', __name__, url_prefix='/tasks')

@bp.route('/list', methods=('GET','POST'))
@login_required
def list():
	page = request.args.get(get_page_parameter(), type=int, default=1)

	if request.method == 'POST':
		name = request.form['s_name']
		name_pattern = "%{}%".format(name)
		tasks = db.paginate(db.select(Task).filter(and_(Task.user_id == g.user.id, Task.name.like(name_pattern))).order_by(Task.created_at.desc()), page=page, per_page=current_app.config['PER_PAGE_PARAMETER'])
	else:	
		tasks = db.paginate(db.select(Task).filter_by(user_id=g.user.id).order_by(Task.created_at.desc()), page=page, per_page=current_app.config['PER_PAGE_PARAMETER'])
	
	items_per_page = current_app.config['PER_PAGE_PARAMETER']
	display_msg = get_localized_msg(lazy_gettext('tasks'), page, tasks.total, items_per_page)
	pagination = Pagination(page=page, total=tasks.total, per_page=items_per_page, display_msg=display_msg)

	return render_template('task/list.html', tasks=tasks, pagination=pagination)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
	task = Task()
	task.finished = False
	form = TaskForm(request.form, obj=task)
	error = None

	if request.method == 'POST' and form.validate():
		try:
			form.populate_obj(task)
			task.user_id = g.user.id
			task.duration = float(task.duration) * 60
			db.session.add(task)
			db.session.commit()
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = lazy_gettext('Task was not created. Database Error')
		else:
			flash(lazy_gettext('Task was successfully created'), 'success')
			return redirect(url_for('task.list'))

	if form.errors:	
		error = process_form_errors(form.errors)

	if error is not None:
		flash(error, 'danger')

	return render_template('task/create.html', form=form, task=task)

def get_task_id(id, check_owner=True):
	task = db.session.execute(db.select(Task).filter_by(id=id)).first()
	if task is None:
		abort(404, lazy_gettext('Task id ') + str(id) + lazy_gettext(" doesn't exist."))

	if check_owner and task[0].user_id != g.user.id:
		abort(403)

	return task[0]

@bp.route('/update/<int:id>', methods=('GET', 'POST'))
@login_required
def update(id):
	task = get_task_id(id)
	task.duration /= 60
	form = TaskForm(request.form, obj=task)
	error = None
	if request.method == 'POST' and form.validate():
		try:
			form.populate_obj(task)
			task.duration = float(task.duration) * 60
			task.last_updated_at = datetime.utcnow()
			db.session.commit()	
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = lazy_gettext('Task was not updated. Database Error')
		else:
			flash(lazy_gettext('Task was successfully updated'), 'success')
			return redirect(url_for('task.list'))

	if form.errors:	
		error = process_form_errors(form.errors)

	if error is not None:
		flash(error, 'danger')

	return render_template('task/update.html', form=form, task=task)

@bp.route('/delete/<int:id>', methods=('POST',))
@login_required
def delete(id):
	task = get_task_id(id)
	if request.method == 'POST':
		error = None
		try:
			db.session.delete(task)
			db.session.commit()
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = lazy_gettext('Task was not deleted. Database Error')
			current_app.logger.warning(e)
		else:
			flash(lazy_gettext('Task was successfully deleted'), 'success')

		if error is not None:
			flash(error, 'danger')

	
	return redirect(url_for('task.list'))

@bp.route('/get_task_duration/<int:id>', methods=('GET',))
def get_task_duration(id):
	task = get_task_id(id)
	return str(task.duration)