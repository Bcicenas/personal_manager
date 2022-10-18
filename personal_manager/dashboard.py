from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from personal_manager.auth import login_required
from personal_manager.db import get_db

bp = Blueprint('dashboard', __name__)

@bp.route('/')
def index():
	if g.user is None:
		return redirect(url_for('auth.login'))
	return render_template('dashboard/index.html')
