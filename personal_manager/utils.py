from datetime import datetime
import calendar

def get_current_year():
	return datetime.now().strftime('%Y')

class CustomHTMLCal(calendar.HTMLCalendar):
	# cssclasses = [style + " text-nowrap" for style in
	# 			  calendar.HTMLCalendar.cssclasses]
	# cssclass_month_head = "text-center month-head"
	cssclass_month = "table month calendar-table"
	# cssclass_year = "text-italic lead"
	def __init__(self, day_data=None):
		self.day_data = day_data
		super().__init__()

	def formatday(self, day, weekday):
		"""
		Return a day as a table cell.
		"""
		if day == 0:
			# day outside month
			return '<td class="%s">&nbsp;</td>' % self.cssclass_noday
		else:
			return '<td class="%s">%d %s</td>' % (self.cssclasses[weekday], day, ', '.join(self.day_data[str(day)]))
