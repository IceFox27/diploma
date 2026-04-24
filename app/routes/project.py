from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from ..models.project import Project
from ..models.employee import Employee
from ..models.role import Role
from ..extensions import db

project_bp = Blueprint('project', __name__, url_prefix='/projects')

@project_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.role.name != 'director':
        flash('Только директор может создавать проекты', 'danger')
        return redirect(url_for('work.index'))
    
    # Получаем всех менеджеров из БД
    managers = Employee.query.join(Role).filter(Role.name == 'manager').all()
    
    if request.method == 'GET':
        return render_template('projects/create_project.html', managers=managers)
    
    try:
        name = request.form.get('name')
        address = request.form.get('address')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date') or None
        budget = request.form.get('budget', 0)
        priority = request.form.get('priority', 'medium')
        status = request.form.get('status', 'planning')
        manager_id = request.form.get('manager_id') or None
        
        if not name or not address or not start_date:
            flash('Заполните обязательные поля', 'danger')
            return render_template('projects/create_project.html', managers=managers)
        
        project = Project(
            name=name,
            address=address,
            description=description,
            start_date=start_date,
            end_date=end_date,
            budget=float(budget) if budget else 0,
            priority=priority,
            status=status,
            manager_id=int(manager_id) if manager_id else None,
            director_id=current_user.id,
            created_by_id=current_user.id,
            progress_percent=0
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash(f'Проект "{name}" успешно создан', 'success')
        return redirect(url_for('work.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка: {str(e)}', 'danger')
        return render_template('projects/create_project.html', managers=managers)