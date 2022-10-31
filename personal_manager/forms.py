from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, SelectField, DateField, PasswordField
from wtforms.validators import DataRequired, Email

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

def process_form_errors(errors):
	end_errors = ''

	for key in errors:
		for error in errors[key]:
			end_errors += error + '<br>'

	return end_errors
