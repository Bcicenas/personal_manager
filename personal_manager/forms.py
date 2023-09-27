from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, SelectField, DateField, PasswordField
from wtforms.widgets import TextInput
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from werkzeug.security import check_password_hash
from flask_babel import lazy_gettext, gettext

class PlanForm(FlaskForm):
	name = StringField(lazy_gettext('Name'), validators=[DataRequired(lazy_gettext('Name is required.'))])

class TaskForm(FlaskForm):
	name = StringField(lazy_gettext('Name'), validators=[DataRequired(lazy_gettext('Name is required.'))])
	description = TextAreaField(lazy_gettext('Description'))
	priority = SelectField(lazy_gettext('Priority'), choices=[(0, lazy_gettext('Low')), (1, lazy_gettext('Medium')), (2, lazy_gettext('High'))])
	till_date = DateField(lazy_gettext('Till date'), id="dp", widget=TextInput())
	finished = BooleanField(lazy_gettext('Finished'), render_kw ={'checked':''})

class ShoppingListForm(FlaskForm):
	name = StringField(lazy_gettext('Name'), validators=[DataRequired(lazy_gettext('Name is required.'))])

class ShoppingItemForm(FlaskForm):
	name = StringField(lazy_gettext('Name'), validators=[DataRequired(lazy_gettext('Name is required.'))])

class EmailForm(FlaskForm):
	email = StringField(lazy_gettext('Email'), validators=[DataRequired(lazy_gettext('Email is required')), Email()])

class PasswordForm(FlaskForm):
	password = PasswordField(lazy_gettext('Password'), validators=[DataRequired(lazy_gettext('Password is required.'))])

class PasswordChangeForm(FlaskForm):
	current_password = PasswordField(lazy_gettext('Current Password'), validators=[DataRequired(lazy_gettext('Current Password is required.'))])
	new_password = PasswordField(lazy_gettext('New Password'), validators=[DataRequired(lazy_gettext('New Password is required.'))])
	confirm_new_passord = PasswordField(
		lazy_gettext('Confirm New Password'), 
		validators=[DataRequired(lazy_gettext('Confirm New Password is required.')), EqualTo('new_password', lazy_gettext('Password mismatch'))])

	def __init__(self, user, *args, **kwargs):
		super(PasswordChangeForm, self).__init__(*args, **kwargs)
		self.user = user

	def validate_current_password(self, field):
		if not check_password_hash(self.user.password, field.data):
			raise ValidationError(lazy_gettext('Current Password is invalid'))

class UserUpdateForm(FlaskForm):
	locale = SelectField(lazy_gettext('Language'), choices=[('en', lazy_gettext('English')), ('lt', lazy_gettext('Lithuanian'))])

	def __init__(self, user, *args, **kwargs):
		super(UserUpdateForm, self).__init__(*args, **kwargs)
		self.user = user

def process_form_errors(errors):
	end_errors = ''

	for key in errors:
		for error in errors[key]:
			end_errors += error + '<br>'

	return end_errors
