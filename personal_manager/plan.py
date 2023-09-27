from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from datetime import datetime
from werkzeug.exceptions import abort

from personal_manager.auth import login_required
from .models import User, Plan, PlanTask
from . import db, get_localized_msg
from .forms import PlanForm, process_form_errors
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
import logging
from flask_paginate import Pagination, get_page_parameter
from flask_babel import lazy_gettext

bp = Blueprint('plan', __name__, url_prefix='/plans')

@bp.route('/list', methods=('GET', 'POST'))
@login_required
def list():
	page = request.args.get(get_page_parameter(), type=int, default=1)
	if request.method == 'POST':
		name = request.form['s_name']
		name_pattern = "%{}%".format(name)
		plans = db.paginate(db.select(Plan).filter(and_(Plan.user_id == g.user.id, Plan.name.like(name_pattern))).order_by(Plan.created_at.desc()), page=page, per_page=current_app.config['PER_PAGE_PARAMETER'])
	else:	
		plans = db.paginate(db.select(Plan).filter_by(user_id=g.user.id).order_by(Plan.created_at.desc()), page=page, per_page=current_app.config['PER_PAGE_PARAMETER'])
	items_per_page = current_app.config['PER_PAGE_PARAMETER']
	display_msg = get_localized_msg(lazy_gettext('plans'), page, plans.total, items_per_page)
	pagination = Pagination(page=page, total=plans.total, per_page=items_per_page, display_msg=display_msg)
	return render_template('plan/list.html', plans=plans, pagination=pagination)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
	plan = Plan()
	form = PlanForm(request.form, obj=plan)
	error = None
	if request.method == 'POST' and form.validate():
		try:
			form.populate_obj(plan)
			plan.user_id = g.user.id
			db.session.add(plan)
			db.session.commit()	
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = lazy_gettext('Plan was not created. Database Error')
		else:
			flash(lazy_gettext('Plan was successfully created'), 'success')
			return redirect(url_for('plan.list'))

	if form.errors:	
		error = process_form_errors(form.errors)

	if error is not None:
		flash(error, 'danger')

	return render_template('plan/create.html', form=form)

def get_plan_id(id, check_owner=True):
	plan = db.session.execute(db.select(Plan).filter_by(id=id)).first()
	if plan is None:
		abort(404, lazy_gettext('Plan id ') + str(id) + lazy_gettext(" doesn't exist."))

	if check_owner and plan[0].user_id != g.user.id:
		abort(403)

	return plan[0]

@bp.route('/update/<int:id>', methods=('GET', 'POST'))
@login_required
def update(id):
	plan = get_plan_id(id)
	form = PlanForm(request.form, obj=plan)
	error = None
	if request.method == 'POST' and form.validate():
		try:
			form.populate_obj(plan)
			plan.last_updated_at = datetime.utcnow()
			db.session.commit()	
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = lazy_gettext('Plan was not updated. Database Error')
		else:
			flash(lazy_gettext('Plan was successfully updated'), 'success')
			return redirect(url_for('plan.list'))

	if form.errors:	
		error = process_form_errors(form.errors)

	if error is not None:
		flash(error, 'danger')

	return render_template('plan/update.html', plan=plan, form=form)

@bp.route('/delete/<int:id>', methods=('POST',))
@login_required
def delete(id):
	plan = get_plan_id(id)
	if request.method == 'POST':
		error = None
		try:
			db.session.delete(plan)
			db.session.commit()
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = lazy_gettext('Plan was not deleted. Database Error')
			current_app.logger.warning(e)
		else:
			flash(lazy_gettext('Plan was successfully deleted'), 'success')

		if error is not None:
			flash(error, 'danger')

	
	return redirect(url_for('plan.list'))
