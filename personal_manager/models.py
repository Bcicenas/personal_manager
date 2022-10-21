from . import db
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from flask import current_app

class User(db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(255), unique=True, nullable=False)
	email = db.Column(db.String(255), unique=True, nullable=False)
	password = db.Column(db.String(255), nullable=False)
	shopping_lists = db.relationship("ShoppingList", back_populates="user", cascade="all, delete-orphan")

class ShoppingList(db.Model):
	__tablename__ = "shopping_lists"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
	created_at = db.Column(db.DateTime(), default=datetime.utcnow)
	last_updated_at = db.Column(db.DateTime(), default=datetime.utcnow)

	user = db.relationship("User", back_populates="shopping_lists")
	shopping_items = db.relationship("ShoppingItem", back_populates="shopping_list", cascade="all, delete-orphan")

	@hybrid_property
	def created_at_in_local_tz(self):
		return self.created_at.replace(tzinfo=current_app.config['UTC-TZ']).astimezone(current_app.config['LOCAL-TZ']).strftime(current_app.config['DATE-FORMAT'])

	@hybrid_property
	def last_updated_at_in_local_tz(self):
		return self.last_updated_at.replace(tzinfo=current_app.config['UTC-TZ']).astimezone(current_app.config['LOCAL-TZ']).strftime(current_app.config['DATE-FORMAT'])

class ShoppingItem(db.Model):
	__tablename__ = "shopping_items"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255), nullable=False)
	shopping_list_id = db.Column(db.Integer, db.ForeignKey("shopping_lists.id"), nullable=False)
	created_at = db.Column(db.DateTime(), default=datetime.utcnow)
	last_updated_at = db.Column(db.DateTime(), default=datetime.utcnow)
	
	shopping_list = db.relationship("ShoppingList", back_populates="shopping_items")