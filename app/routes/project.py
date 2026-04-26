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
    
@project_bp.route('/<int:project_id>')
@login_required
def view(project_id):
    project = Project.query.get_or_404(project_id)
    
    if current_user.role.name == 'director':
        pass
    elif current_user.role.name == 'manager':
        if project.manager_id != current_user.id and project.director_id != current_user.id:
            flash('У вас нет доступа к этому проекту', 'danger')
            return redirect(url_for('work.index'))
    else:
        if not current_user.assigned_projects.filter(Project.id == project_id).first():
            flash('У вас нет доступа к этому проекту', 'danger')
            return redirect(url_for('work.index'))
    
    return render_template('projects/project_detail.html', project=project)


@project_bp.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Проверка прав: директор или менеджер проекта
    if current_user.role.name != 'director' and project.manager_id != current_user.id:
        flash('У вас нет прав для редактирования этого проекта', 'danger')
        return redirect(url_for('work.index'))
    
    if request.method == 'GET':
        managers = Employee.query.join(Role).filter(Role.name == 'manager').all()
        return render_template('projects/edit_project.html', project=project, managers=managers)
    
    try:
        project.name = request.form.get('name')
        project.address = request.form.get('address')
        project.description = request.form.get('description')
        project.start_date = request.form.get('start_date')
        project.end_date = request.form.get('end_date') or None
        project.budget = float(request.form.get('budget', 0))
        project.priority = request.form.get('priority', 'medium')
        project.status = request.form.get('status', 'planning')
        
        if current_user.role.name == 'director':
            manager_id = request.form.get('manager_id')
            project.manager_id = int(manager_id) if manager_id else None
        
        db.session.commit()
        flash(f'Проект "{project.name}" успешно обновлён', 'success')
        return redirect(url_for('project.view', project_id=project.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка: {str(e)}', 'danger')
        managers = Employee.query.join(Role).filter(Role.name == 'manager').all()
        return render_template('projects/edit_project.html', project=project, managers=managers)


@project_bp.route('/<int:project_id>/assign-workers', methods=['GET', 'POST'])
@login_required
def assign_workers(project_id):
    project = Project.query.get_or_404(project_id)
    
    if current_user.role.name != 'director' and project.manager_id != current_user.id:
        flash('Только менеджер проекта или директор могут назначать сотрудников', 'danger')
        return redirect(url_for('project.view', project_id=project_id))
    
    if request.method == 'GET':
        workers = Employee.query.join(Role).filter(Role.name == 'employee').all()
        current_worker_ids = [w.id for w in project.workers]
        
        return render_template('projects/assign_workers.html', 
                              project=project, 
                              workers=workers,
                              current_worker_ids=current_worker_ids)
    
    try:
        worker_ids = request.form.getlist('worker_ids')
        project.workers = []
        
        for worker_id in worker_ids:
            worker = Employee.query.get(worker_id)
            if worker:
                project.workers.append(worker)
        
        db.session.commit()
        flash('Состав рабочей группы обновлён', 'success')
        return redirect(url_for('project.view', project_id=project_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка: {str(e)}', 'danger')
        return redirect(url_for('project.assign_workers', project_id=project_id))