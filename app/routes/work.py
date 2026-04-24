from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify
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
    from ..models.project import Project
    
    all_employees = Employee.query.all()
    managers_count = Employee.query.join(Role).filter(Role.name == 'manager').count()
    employees_count = Employee.query.join(Role).filter(
        Role.name != 'director', 
        Role.name != 'manager'
    ).count()
    
    active_threshold = datetime.utcnow() - timedelta(seconds=300)
    active_employees = Employee.query.filter(Employee.last_seen >= active_threshold).all()
    active_count = len(active_employees)
    
    if current_user.role.name == 'director':
        projects = Project.query.all()
    elif current_user.role.name == 'manager':
        projects = Project.query.filter(
            (Project.manager_id == current_user.id) |
            (Project.director_id == current_user.id)
        ).all()
    else:
        projects = current_user.assigned_projects.all()

    return render_template('work.html', 
                         employees=all_employees, 
                         managers_count=managers_count,
                         employees_count=employees_count, 
                         active_employees=active_employees,
                         active_count=active_count,
                         projects=projects,
                         now=datetime.utcnow())

@work_bp.route('/employee/<int:employee_id>/fire', methods=['POST'])
@login_required
def fire_employee(employee_id):
    if current_user.role.name != 'director':
        return jsonify({'success': False, 'error': 'Нет прав'}), 403
    
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({'success': False, 'error': 'Сотрудник не найден'}), 404
    
    if employee.id == current_user.id:
        return jsonify({'success': False, 'error': 'Нельзя уволить самого себя'}), 400
    
    try:
        db.session.delete(employee)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
@work_bp.route('/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    if current_user.role.name != 'director':
        return jsonify({'success': False, 'error': 'Нет прав'}), 403
    
    from ..models.project import Project
    
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'success': False, 'error': 'Проект не найден'}), 404
    
    try:
        db.session.delete(project)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500