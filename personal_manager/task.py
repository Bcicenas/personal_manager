from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from datetime import datetime
from werkzeug.exceptions import abort

from personal_manager.auth import login_required
from .models import User, ShoppingList, Task
from . import db
from sqlalchemy.exc import IntegrityError

bp = Blueprint('task', __name__, url_prefix='/tasks')

@bp.route('/list')
@login_required
def list():
	tasks = db.session.execute(
		db.select(Task).filter_by(user_id=g.user.id).order_by(Task.created_at.desc())
	).fetchall()
	return render_template('task/list.html', tasks=tasks)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
	if request.method == 'POST':
		error = None

		try:
			task = Task(name=request.form['name'], 
				description=request.form['description'],
				priority=request.form['priority'],
				user_id=g.user.id)
			db.session.add(task)
			db.session.commit()	
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = f"Shopping List was not created. Database Error"
		else:
			flash('Shopping List was successfully created', 'success')
			return redirect(url_for('task.list'))

		if error is not None:
			flash(error, 'danger')

	return render_template('task/create.html')

def get_task_id(id, check_owner=True):
	task = db.session.execute(db.select(Task).filter_by(id=id)).first()
	if task is None:
		abort(404, f"Task id {id} doesn't exist.")

	if check_owner and task[0].user_id != g.user.id:
		abort(403)

	return task[0]

@bp.route('/update/<int:id>', methods=('GET', 'POST'))
@login_required
def update(id):
	task = get_task_id(id)

	if request.method == 'POST':
		try:
			task.name = request.form['name']
			task.description = request.form['description']
			task.priority = request.form['priority']
			task.last_updated_at = datetime.utcnow()
			db.session.commit()	
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = f"Task was not updated. Database Error"
		else:
			flash('Task was successfully updated', 'success')
			return redirect(url_for('task.list'))

		if error is not None:
			flash(error, 'danger')

	return render_template('task/update.html', task=task)

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
			error = f"Task was not deleted. Database Error"
			current_app.logger.warning(e)
		else:
			flash('Task was successfully deleted', 'success')

		if error is not None:
			flash(error, 'danger')

	
	return redirect(url_for('task.list'))