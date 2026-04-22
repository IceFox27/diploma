from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime

from ..extensions import db
from ..models.project import Project
from ..models.employee import Employee

work_bp = Blueprint('work', __name__, url_prefix='/work')

@work_bp.route('/')
@login_required
def index():
    if current_user.role.name == 'director':
        projects = Project.query.all()
    elif current_user.role.name == 'manager':
        projects = Project.query.filter(
            (Project.manager_id == current_user.id) |
            (Project.director_id == current_user.id)
        ).all()
    else:
        projects = current_user.assigned_projects.all()
    
    projects_count = len(projects)
    team_count = Employee.query.count()
    
    return render_template('work.html',
                         now=datetime.now(),
                         recent_projects=projects[:6] if projects else [],
                         projects_count=projects_count,
                         team_count=team_count,
                         recent_tasks=[],      
                         tasks_completed=0,    
                         tasks_pending=0)      


@work_bp.route('/projects')
@login_required
def projects():
    if current_user.role.name == 'director':
        projects = Project.query.all()
    elif current_user.role.name == 'manager':
        projects = Project.query.filter(
            (Project.manager_id == current_user.id) |
            (Project.director_id == current_user.id)
        ).all()
    else:
        projects = current_user.assigned_projects.all()
    
    return render_template('work_projects.html', projects=projects)