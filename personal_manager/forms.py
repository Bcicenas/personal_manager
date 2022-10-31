from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, SelectField, DateField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from werkzeug.security import check_password_hash

class TaskForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired('Name is required.')])
	description = TextAreaField('Description')
	priority = SelectField(choices=[(0, 'Low'), (1, 'Medium'), (2, 'High')])
	till_date = DateField('Till date')
	finished = BooleanField('Finished', render_kw ={'checked':''})

class ShoppingListForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired('Name is required.')])

class ShoppingItemForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired('Name is required.')])

class EmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired('Password is required.')])

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired('Current Password is required.')])
    new_password = PasswordField('New Password', validators=[DataRequired('New Password is required.')])
    confirm_new_passord = PasswordField('Confirm New Password', validators=[DataRequired('Confirm New Password is required.'), EqualTo('new_password', 'Password mismatch')])

    def __init__(self, user, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate_current_password(self, field):
        if not check_password_hash(self.user.password, field.data):
            raise ValidationError('Current Password is invalid')

def process_form_errors(errors):
	end_errors = ''

	for key in errors:
		for error in errors[key]:
			end_errors += error + '<br>'

	return end_errors
