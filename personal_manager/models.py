from . import db
from . import mail
from . import convert_date_time
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from flask import current_app, render_template, url_for
import re
from password_strength import PasswordPolicy
from werkzeug.security import generate_password_hash
from flask_mail import Message
from flask_babel import lazy_gettext

# User model
class User(db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(255), unique=True, nullable=False)
	email = db.Column(db.String(255), unique=True, nullable=False)
	password = db.Column(db.String(255), nullable=False)
	locale = db.Column(db.String(50), nullable=False, default='en')
	email_confirmed = db.Column(db.Boolean(255), default=False)
	shopping_lists = db.relationship("ShoppingList", back_populates="user", cascade="all, delete")
	tasks = db.relationship("Task", back_populates="user", cascade="all, delete")

	@validates("username")
	def validate_username(self, key, username):
		if not username:
			raise ValueError(lazy_gettext('Username is required.'))

		return username

	@validates("email")
	def validate_email(self, key, address):
		pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
		if not re.match(pat, address):
			raise ValueError(lazy_gettext("Email is invalid"))
		return address

	@validates("password")
	def validate_password(self, key, password):
		if not password:
			raise ValueError(lazy_gettext('Password is required.'))

		policy = PasswordPolicy.from_names(
			length=8,
			uppercase=1,
			numbers=1,
			special=1,
		)

		if policy.test(password):
			raise ValueError(lazy_gettext('Please choose a stronger password.') +
				'<br>' + lazy_gettext('Must contain at least 8 characters') +
				'<br>' + lazy_gettext('Must contain at least 1 uppercase letter') +
				'<br>' + lazy_gettext('Must contain at least 1 number') +
				'<br>' + lazy_gettext('Must contain at least 1 special character'))
			
		return generate_password_hash(password)


	def send_email_confirmation(self, ts):
		email_msg = Message()
		email_msg.subject = lazy_gettext("Confirm your email")
		email_msg.add_recipient(self.email)

		token = ts.dumps(self.email, salt=current_app.config['EMAIL_CONFIRM_SALT'])
		confirm_url = url_for('auth.confirm_email', token=token,_external=True)

		email_msg.html = render_template('auth/activate.html', confirm_url=confirm_url)

		mail.send(email_msg)


	def send_password_reset(self, ts):
		email_msg = Message()
		email_msg.subject = lazy_gettext("Password Reset")
		email_msg.add_recipient(self.email)

		token = ts.dumps(self.email, salt=current_app.config['EMAIL_CONFIRM_SALT'])
		reset_url = url_for('auth.reset_password', token=token,_external=True)

		email_msg.html = render_template('auth/password_reset_link.html', reset_url=reset_url)

		mail.send(email_msg)

		

class ShoppingList(db.Model):
	__tablename__ = "shopping_lists"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	created_at = db.Column(db.DateTime(), default=datetime.utcnow)
	last_updated_at = db.Column(db.DateTime(), default=datetime.utcnow)

	user = db.relationship("User", back_populates="shopping_lists")
	shopping_items = db.relationship("ShoppingItem", back_populates="shopping_list", cascade="all, delete")

	@hybrid_property
	def created_at_in_local_tz(self):
		return convert_date_time(self.created_at, 'UTC_TZ', 'LOCAL_TZ')

	@hybrid_property
	def last_updated_at_in_local_tz(self):
		return convert_date_time(self.last_updated_at, 'UTC_TZ', 'LOCAL_TZ')


	@validates("name")
	def validate_name(self, key, name):
		if not name:
			raise ValueError(lazy_gettext('Name is required.'))

		return name

class ShoppingItem(db.Model):
	__tablename__ = "shopping_items"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255), nullable=False)
	shopping_list_id = db.Column(db.Integer, db.ForeignKey("shopping_lists.id", ondelete="CASCADE"), nullable=False)
	created_at = db.Column(db.DateTime(), default=datetime.utcnow)
	last_updated_at = db.Column(db.DateTime(), default=datetime.utcnow)
	
	shopping_list = db.relationship("ShoppingList", back_populates="shopping_items")

	@validates("name")
	def validate_name(self, key, name):
		if not name:
			raise ValueError(lazy_gettext('Name is required.'))

		return name


class Task(db.Model):
	__tablename__ = "tasks"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255), nullable=False)
	description = db.Column(db.Text, nullable=True)
	# priority - 0 low, 1 - medium, 2 - high 
	priority = db.Column(db.SmallInteger, default=0)
	user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	# 0 to 1440(0 to 24h) in minutes
	duration = db.Column(db.Integer, default=0)
	created_at = db.Column(db.DateTime(), default=datetime.utcnow)
	last_updated_at = db.Column(db.DateTime(), default=datetime.utcnow)
	
	user = db.relationship("User", back_populates="tasks")

	@hybrid_property
	def priority_name(self):
		if self.priority == 0:
			return lazy_gettext('Low')
		elif self.priority == 1:
			return lazy_gettext('Medium')
		else:
			return lazy_gettext('High')	

	@hybrid_property
	def priority_in_css_class(self):
		if self.priority == 0:
			return 'primary'
		elif self.priority == 1:
			return 'secondary'
		else:
			return 'danger'

	@hybrid_property
	def created_at_in_local_tz(self):
		return convert_date_time(self.created_at, 'UTC_TZ', 'LOCAL_TZ')

	@hybrid_property
	def last_updated_at_in_local_tz(self):
		return convert_date_time(self.last_updated_at, 'UTC_TZ', 'LOCAL_TZ')


class Plan(db.Model):
	__tablename__ = "plans"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255), nullable=False)
	created_at = db.Column(db.DateTime(), default=datetime.utcnow)
	last_updated_at = db.Column(db.DateTime(), default=datetime.utcnow)
	plan_date = db.Column(db.DateTime(), default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	plan_tasks = db.relationship("PlanTask", back_populates="plan", cascade="all, delete", lazy="dynamic", order_by='PlanTask.start_time')	

	@hybrid_property
	def created_at_in_local_tz(self):
		return convert_date_time(self.created_at, 'UTC_TZ', 'LOCAL_TZ')

	@hybrid_property
	def plan_date_in_local_tz(self):
		return convert_date_time(self.plan_date, 'UTC_TZ', 'LOCAL_TZ')

	@hybrid_property
	def last_updated_at_in_local_tz(self):
		return convert_date_time(self.last_updated_at, 'UTC_TZ', 'LOCAL_TZ')

class PlanTask(db.Model):
	__tablename__ = "plan_tasks"
	id = db.Column(db.Integer, primary_key=True)
	created_at = db.Column(db.DateTime(), default=datetime.utcnow)
	last_updated_at = db.Column(db.DateTime(), default=datetime.utcnow)
	# time - 0 to 24h
	start_time = db.Column(db.SmallInteger, default=0)
	plan_id = db.Column(db.Integer, db.ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)	
	task_id = db.Column(db.Integer, db.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)	

	plan = db.relationship("Plan", back_populates="plan_tasks")
	task = db.relationship("Task")

	@hybrid_property
	def created_at_in_local_tz(self):
		return convert_date_time(self.created_at, 'UTC_TZ', 'LOCAL_TZ')

	@hybrid_property
	def last_updated_at_in_local_tz(self):
		return convert_date_time(self.last_updated_at, 'UTC_TZ', 'LOCAL_TZ')
