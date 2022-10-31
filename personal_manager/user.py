from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, current_app, session
)
from datetime import datetime
from werkzeug.exceptions import abort

from personal_manager.auth import login_required
from .models import User
from .forms import PasswordChangeForm, process_form_errors
from . import db
from sqlalchemy.exc import IntegrityError
import logging
bp = Blueprint('user', __name__, url_prefix='/users')

@bp.route('/personal_details')
@login_required
def personal_details():
	return render_template('user/personal_details.html', user=g.user)


@bp.route('/change_password', methods=('GET', 'POST'))
@login_required
def change_password():
	error = None
	form = PasswordChangeForm(g.user)

	if request.method == 'POST' and form.validate_on_submit():
		user = g.user

		try:
			user.password = form.new_password.data
			db.session.commit()
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = f"Password change failed. Database Error"
		else:
			flash('Password was successfully changed', 'success')
			return redirect(url_for('user.personal_details'))

	if form.errors:	
		error = process_form_errors(form.errors)

	if error is not None:
		flash(error, 'danger')

	return render_template('user/change_password.html', form=form)

@bp.route('/delete_account', methods=('POST',))
@login_required
def delete_account():
	error = None
	user = User.query.filter_by(id=g.user.id).first_or_404()
	if request.method == 'POST':
		try:
			db.session.delete(user)
			db.session.commit()
		except ValueError as e:
			error = f"{e}"
		except IntegrityError as e:
			error = f"Account was not deleted. Database Error"
		else:
			g.user = None
			session.clear()
			flash('Account was successfully deleted', 'success')
			return redirect(url_for('dashboard.index'))

	if error is not None:
		flash(error, 'danger')

	return redirect(url_for('user.personal_details'))

@bp.route('/set_locale')
def set_locale():
	session['locale'] = request.args.get('locale')
	return redirect(url_for('dashboard.index'))