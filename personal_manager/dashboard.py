from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
from flask import session
from personal_manager.auth import login_required
from . models import User, ShoppingList, Task, Plan
from . import db, parsed_locale

import calendar
from .utils import CustomHTMLCal
from datetime import datetime

bp = Blueprint('dashboard', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
	if g.user is None:
		return render_template('landing_page.html')
	
	# calendar
	if 'calendar-date' not in session:
		session['calendar-date'] = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')
	else:
		if request.form.get('calendar-date') is not None:
			session['calendar-date'] = datetime.strptime(request.form.get('calendar-date'), '%Y-%m-%d')



	# if next or prev month btn is pressed
	if request.args.get('month_select') is not None:
		if request.args.get('month_select') == 'next':
			if session['calendar-date'].month + 1 == 13:
				month_to_replace = 1
				year_to_replace = session['calendar-date'].year + 1
			else:
				month_to_replace = session['calendar-date'].month + 1
				year_to_replace = session['calendar-date'].year

			day_to_replace = calendar.monthrange(session['calendar-date'].year, month_to_replace)[1]

			session['calendar-date'] = session['calendar-date'].replace(year=year_to_replace, month=month_to_replace, day=day_to_replace)
		elif request.args.get('month_select') == 'prev':
			if session['calendar-date'].month - 1 == 0:
				month_to_replace = 12
				year_to_replace = session['calendar-date'].year - 1
			else:
				month_to_replace = session['calendar-date'].month - 1
				year_to_replace = session['calendar-date'].year

			day_to_replace = calendar.monthrange(session['calendar-date'].year, month_to_replace)[1]

			session['calendar-date'] = session['calendar-date'].replace(year=year_to_replace, month=month_to_replace, day=day_to_replace)
	
	year = session['calendar-date'].year
	month = session['calendar-date'].month

	# get month plans for calendar
	# last day for query
	day_range = calendar.monthrange(year, month)
	start_day = datetime(year, month, 1)
	end_day = datetime(year, month, day_range[1])
	plans = db.session.execute(
		db.select(Plan).filter(Plan.plan_date.between(start_day, end_day), Plan.user_id==g.user.id)
	).fetchall()
	
	plan_data = {}
	for i in range(day_range[1]):
		plan_data [str(i + 1)] = []

	for plan in plans:
		plan_data[str(plan[0].plan_date.day)].append('<a href="%s">%s<a>' % (url_for('plan.update', id=plan[0].id), plan[0].name))

	this_month_calendar = CustomHTMLCal(day_data=plan_data, locale=parsed_locale()).formatmonth(year, month)

	daily_plans = db.session.execute(
		db.select(Plan).filter(Plan.plan_date == session['calendar-date'], Plan.user_id==g.user.id)
	).fetchall()

	# # shopping lists
	# shopping_lists = db.session.execute(
	# 	db.select(ShoppingList).filter_by(user_id=g.user.id).order_by(ShoppingList.created_at.desc()).limit(10)
	# ).fetchall()

	# # tasks
	# tasks = db.session.execute(
	# 	db.select(Task).filter_by(user_id=g.user.id).order_by(Task.created_at.desc()).limit(10)
	# ).fetchall()

	return render_template('dashboard/index.html', calendar=this_month_calendar, daily_plans=daily_plans, end_day=day_range[1], plan_data=plan_data)
