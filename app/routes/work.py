from datetime import datetime, timedelta
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from ..extensions import db
from ..models.employee import Employee
from ..models.role import Role

work_bp = Blueprint('work', __name__, url_prefix='/work')

@work_bp.before_app_request
def update_last_seen():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@work_bp.route('/')
@login_required
def index():
    all_employees = Employee.query.all()
    managers_count = Employee.query.join(Role).filter(Role.name == 'manager').count()
    employees_count = Employee.query.join(Role).filter(
        Role.name != 'director', 
        Role.name != 'manager'
    ).count()
    
    active_threshold = datetime.utcnow() - timedelta(seconds=5)
    active_employees = Employee.query.filter(Employee.last_seen >= active_threshold).all()
    active_count = len(active_employees)

    return render_template('work.html', 
                       employees=all_employees, 
                       managers_count=managers_count,
                       employees_count=employees_count, 
                       active_employees=active_employees,
                       active_count=active_count,
                       now=datetime.utcnow())