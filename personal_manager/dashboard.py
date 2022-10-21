from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort

from personal_manager.auth import login_required
from . models import User, ShoppingList
from . import db

bp = Blueprint('dashboard', __name__)

@bp.route('/')
def index():
	if g.user is None:
		return redirect(url_for('auth.login'))
		
	# shopping lists
	shopping_lists = db.session.execute(
		db.select(ShoppingList).filter_by(user_id=g.user.id).order_by(ShoppingList.created_at)
	).fetchall()

	return render_template('dashboard/index.html', shopping_lists=shopping_lists)
