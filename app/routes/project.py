from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models.project import Project
from ..models.employee import Employee
from ..models.role import Role  # ДОБАВЛЕН ИМПОРТ (был пропущен)

project_bp = Blueprint('project', __name__, url_prefix='/projects')


@project_bp.route('/')
@login_required
def list_projects():
    """Список всех проектов (директор видит все, менеджер/сотрудник - свои)"""
    if current_user.role.name == 'director':
        projects = Project.query.all()
    elif current_user.role.name == 'manager':
        projects = Project.query.filter(
            (Project.manager_id == current_user.id) | 
            (Project.director_id == current_user.id)
        ).all()
    else:
        # Обычный сотрудник - проекты, где он в рабочей группе
        # assigned_projects теперь динамический (lazy='dynamic'), можно использовать .all()
        projects = current_user.assigned_projects.all()
    
    return render_template('projects/list.html', projects=projects)


@project_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Создание проекта (только для директора)"""
    # Проверка прав: только директор может создавать проекты
    if current_user.role.name != 'director':
        flash('Только директор может создавать проекты', 'danger')
        return redirect(url_for('project.list_projects'))
    
    # GET-запрос: показываем форму
    if request.method == 'GET':
        managers = Employee.query.join(Role).filter(Role.name == 'manager').all()
        return render_template('projects/create.html', managers=managers)
    
    # POST-запрос: обрабатываем форму
    try:
        # Получаем данные из формы
        name = request.form.get('name')
        address = request.form.get('address')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date') or None
        budget = request.form.get('budget', 0)
        priority = request.form.get('priority', 'medium')
        manager_id = request.form.get('manager_id') or None
        
        # Валидация обязательных полей
        if not name or not address or not start_date:
            flash('Заполните обязательные поля (название, адрес, дата начала)', 'danger')
            managers = Employee.query.join(Role).filter(Role.name == 'manager').all()
            return render_template('projects/create.html', managers=managers)
        
        # Создаём проект
        project = Project(
            name=name,
            address=address,
            description=description,
            start_date=start_date,
            end_date=end_date,
            budget=float(budget) if budget else 0,
            priority=priority,
            manager_id=int(manager_id) if manager_id else None,
            director_id=current_user.id,
            created_by_id=current_user.id,
            status='planning',
            progress_percent=0
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash(f'Проект "{name}" успешно создан', 'success')
        return redirect(url_for('project.list_projects'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при создании проекта: {str(e)}', 'danger')
        managers = Employee.query.join(Role).filter(Role.name == 'manager').all()
        return render_template('projects/create.html', managers=managers)


@project_bp.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(project_id):
    """Редактирование проекта (только директор или менеджер проекта)"""
    project = Project.query.get_or_404(project_id)
    
    # Проверка прав
    if current_user.role.name != 'director' and project.manager_id != current_user.id:
        flash('У вас нет прав для редактирования этого проекта', 'danger')
        return redirect(url_for('project.list_projects'))
    
    # GET-запрос: показываем форму
    if request.method == 'GET':
        managers = Employee.query.join(Role).filter(Role.name == 'manager').all()
        return render_template('projects/edit.html', project=project, managers=managers)
    
    # POST-запрос: обрабатываем форму
    try:
        # Обновляем данные
        project.name = request.form.get('name')
        project.address = request.form.get('address')
        project.description = request.form.get('description')
        project.start_date = request.form.get('start_date')
        project.end_date = request.form.get('end_date') or None
        project.budget = float(request.form.get('budget', 0))
        project.priority = request.form.get('priority', 'medium')
        project.status = request.form.get('status', 'planning')
        
        # Только директор может менять менеджера
        if current_user.role.name == 'director':
            manager_id = request.form.get('manager_id')
            project.manager_id = int(manager_id) if manager_id else None
        
        db.session.commit()
        flash(f'Проект "{project.name}" успешно обновлён', 'success')
        return redirect(url_for('project.list_projects'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при обновлении: {str(e)}', 'danger')
        managers = Employee.query.join(Role).filter(Role.name == 'manager').all()
        return render_template('projects/edit.html', project=project, managers=managers)


@project_bp.route('/<int:project_id>/delete', methods=['POST'])
@login_required
def delete(project_id):
    """Удаление проекта (только для директора)"""
    if current_user.role.name != 'director':
        flash('Только директор может удалять проекты', 'danger')
        return redirect(url_for('project.list_projects'))
    
    project = Project.query.get_or_404(project_id)
    project_name = project.name
    
    try:
        db.session.delete(project)
        db.session.commit()
        flash(f'Проект "{project_name}" успешно удалён', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении: {str(e)}', 'danger')
    
    return redirect(url_for('project.list_projects'))


@project_bp.route('/<int:project_id>/view')
@login_required
def view(project_id):
    """Просмотр деталей проекта"""
    project = Project.query.get_or_404(project_id)
    
    # Проверка доступа
    if current_user.role.name == 'director':
        pass  # Директор видит всё
    elif current_user.role.name == 'manager':
        if project.manager_id != current_user.id and project.director_id != current_user.id:
            flash('У вас нет доступа к этому проекту', 'danger')
            return redirect(url_for('project.list_projects'))
    else:
        # Обычный сотрудник: проверяем, привязан ли к проекту
        # assigned_projects теперь динамический, используем filter
        if not current_user.assigned_projects.filter(Project.id == project_id).first():
            flash('У вас нет доступа к этому проекту', 'danger')
            return redirect(url_for('project.list_projects'))
    
    return render_template('projects/view.html', project=project)


@project_bp.route('/<int:project_id>/assign-workers', methods=['GET', 'POST'])
@login_required
def assign_workers(project_id):
    """Привязка работников к проекту (только менеджер или директор)"""
    project = Project.query.get_or_404(project_id)
    
    # Проверка прав: менеджер проекта или директор
    if current_user.role.name != 'director' and project.manager_id != current_user.id:
        flash('Только менеджер проекта или директор могут назначать сотрудников', 'danger')
        return redirect(url_for('project.view', project_id=project_id))
    
    # GET-запрос: показываем форму
    if request.method == 'GET':
        # Получаем всех сотрудников (с ролью 'employee')
        workers = Employee.query.join(Role).filter(Role.name == 'employee').all()
        current_worker_ids = [w.id for w in project.workers]
        
        return render_template('projects/assign_workers.html', 
                              project=project, 
                              workers=workers,
                              current_worker_ids=current_worker_ids)
    
    # POST-запрос: обрабатываем назначение
    try:
        worker_ids = request.form.getlist('worker_ids')
        
        # Очищаем текущих работников
        project.workers = []
        
        # Добавляем новых
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