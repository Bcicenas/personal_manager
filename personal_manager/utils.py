from datetime import datetime
import calendar

def get_current_year():
	return datetime.now().strftime('%Y')

class CustomHTMLCal(calendar.LocaleHTMLCalendar):
	# cssclasses = [style + " text-nowrap" for style in
	# 			  calendar.HTMLCalendar.cssclasses]
	# cssclass_month_head = "text-center month-head"
	cssclass_month = "table month calendar-table"
	# cssclass_year = "text-italic lead"
	def __init__(self,day_data=None, **kw):
		self.day_data = day_data
		super().__init__(**kw)

	def formatday(self, day, weekday):
		"""
		Return a day as a table cell.
		"""
		if day == 0:
			# day outside month
			return '<td class="%s">&nbsp;</td>' % self.cssclass_noday
		else:
			return '<td class="%s"><div class="card"><div class="card-header">%d</div> <div class="card-body">%s</div></div></td>' % (self.cssclasses[weekday], day, '<br> '.join(self.day_data[str(day)]))
