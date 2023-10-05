from datetime import datetime
from flask import url_for
from flask_babel import lazy_gettext

import calendar

def get_current_year():
	return datetime.now().strftime('%Y')

class CustomHTMLCal(calendar.LocaleHTMLCalendar):
	# cssclasses = [style + " text-nowrap" for style in
	# 			  calendar.HTMLCalendar.cssclasses]
	# cssclass_month_head = "text-center month-head"
	cssclass_month = "table table-bordered month calendar-table"
	# cssclass_year = "text-italic lead"
	def __init__(self, year, month, day_data=None, **kw):
		self.day_data = day_data
		self.year = year
		self.month = month
		super().__init__(**kw)

	def formatday(self, day, weekday):
		"""
		Return a day as a table cell.
		"""
		if day == 0:
			# day outside month
			return '<td class="%s">&nbsp;</td>' % self.cssclass_noday
		else:
			if not self.day_data[str(day)]:
				return '<td class="%s"><div class="card"><div class="card-header">%d</div> <div class="card-body"><a href="%s" class="btn btn-success" role="button">%s</a></div></div></td>' % (self.cssclasses[weekday], day, url_for('plan.create', plan_date=datetime(self.year, self.month, day).strftime('%Y-%m-%d')), lazy_gettext('Add New'))
			else:
				return '<td class="%s"><div class="card"><div class="card-header">%d</div> <div class="card-body">%s</div></div></td>' % (self.cssclasses[weekday], day, '<br> '.join(self.day_data[str(day)]))
