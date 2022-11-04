from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from datetime import datetime
from werkzeug.exceptions import abort

from personal_manager.auth import login_required
from .models import Task
from .forms import TaskForm, process_form_errors
from . import db
from sqlalchemy.exc import IntegrityError
from flask_paginate import Pagination, get_page_parameter
from flask_babel import lazy_gettext

bp = Blueprint('task', __name__, url_prefix='/tasks')

@bp.route('/list', methods=('GET',))
@login_required
def list():
	page = request.args.get(get_page_parameter(), type=int, default=1)
	tasks = db.paginate(db.select(Task).filter_by(user_id=g.user.id).order_by(Task.created_at.desc()), page=page, per_page=current_app.config['PER_PAGE_PARAMETER'])
	pagination = Pagination(page=page, total=tasks.total, per_page=current_app.config['PER_PAGE_PARAMETER'], record_name='tasks')

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
	form = TaskForm(request.form, obj=task)
	error = None
	if request.method == 'POST' and form.validate():
		try:
			form.populate_obj(task)
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
	