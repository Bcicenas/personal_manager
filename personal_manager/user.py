from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from datetime import datetime
from werkzeug.exceptions import abort

from personal_manager.auth import login_required
from .models import User
from . import db
from sqlalchemy.exc import IntegrityError

bp = Blueprint('user', __name__, url_prefix='/users')

@bp.route('/personal_details')
@login_required
def personal_details():
	return render_template('user/personal_details.html', user=g.user)
