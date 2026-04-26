from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from ..models.project import Project
from ..models.employee import Employee
from ..models.role import Role
from ..extensions import db
from ..models.task import Task
from datetime import datetime
from ..functions import save_task_files

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
    
    # Проверка доступа
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
    
    # Получаем задачи проекта
    tasks = Task.query.filter_by(project_id=project_id).order_by(Task.created_at.desc()).all()
    
    # Подсчёт статистики по задачам
    tasks_total = len(tasks)
    tasks_completed = Task.query.filter_by(project_id=project_id, status='completed').count()
    tasks_in_progress = Task.query.filter_by(project_id=project_id, status='in_progress').count()
    tasks_pending = Task.query.filter_by(project_id=project_id, status='pending').count()
    
    return render_template('projects/project_detail.html', 
                         project=project, 
                         tasks=tasks,
                         tasks_total=tasks_total,
                         tasks_completed=tasks_completed,
                         tasks_in_progress=tasks_in_progress,
                         tasks_pending=tasks_pending)


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
    
@project_bp.route('/<int:project_id>/task/create', methods=['GET', 'POST'])
@login_required
def create_task(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Проверка прав: менеджер проекта или директор
    if current_user.role.name != 'director' and project.manager_id != current_user.id:
        flash('Только менеджер проекта или директор могут создавать задачи', 'danger')
        return redirect(url_for('project.view', project_id=project_id))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority', 'medium')
        deadline = request.form.get('deadline') or None
        assignee_id = request.form.get('assignee_id') or None
        
        if not title:
            flash('Название задачи обязательно', 'danger')
            return redirect(url_for('project.create_task', project_id=project_id))
        
        task = Task(
            title=title,
            description=description,
            priority=priority,
            deadline=deadline,
            project_id=project_id,
            assigner_id=current_user.id,
            assignee_id=int(assignee_id) if assignee_id else None
        )
        
        try:
            db.session.add(task)
            db.session.commit()
            flash('Задача успешно создана', 'success')
            return redirect(url_for('project.view', project_id=project_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'danger')
    
    # GET запрос — показываем форму
    workers = project.workers.all()
    return render_template('projects/create_task.html', project=project, workers=workers)


@project_bp.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.project
    
    # Проверка прав
    if current_user.role.name != 'director' and project.manager_id != current_user.id and task.assignee_id != current_user.id:
        flash('У вас нет прав для редактирования этой задачи', 'danger')
        return redirect(url_for('project.view', project_id=project.id))
    
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.priority = request.form.get('priority', 'medium')
        task.status = request.form.get('status', 'pending')
        task.deadline = request.form.get('deadline') or None
        assignee_id = request.form.get('assignee_id')
        task.assignee_id = int(assignee_id) if assignee_id else None
        
        if task.status == 'completed' and not task.completed_at:
            task.completed_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Задача обновлена', 'success')
            return redirect(url_for('project.view', project_id=project.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'danger')
    
    workers = project.workers.all()
    return render_template('projects/edit_task.html', task=task, project=project, workers=workers)


@project_bp.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project_id = task.project_id
    
    if current_user.role.name != 'director' and task.project.manager_id != current_user.id:
        flash('У вас нет прав для удаления этой задачи', 'danger')
        return redirect(url_for('project.view', project_id=project_id))
    
    try:
        db.session.delete(task)
        db.session.commit()
        flash('Задача удалена', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка: {str(e)}', 'danger')
    
    return redirect(url_for('project.view', project_id=project_id))


@project_bp.route('/task/<int:task_id>/status/<status>')
@login_required
def change_task_status(task_id, status):
    task = Task.query.get_or_404(task_id)
    
    # Проверка прав: директор, менеджер проекта или исполнитель задачи
    if current_user.role.name != 'director' and task.project.manager_id != current_user.id and task.assignee_id != current_user.id:
        flash('У вас нет прав', 'danger')
        return redirect(url_for('project.view', project_id=task.project_id))
    
    if status not in ['pending', 'in_progress', 'completed', 'cancelled']:
        flash('Неверный статус', 'danger')
        return redirect(url_for('project.view', project_id=task.project_id))
    
    task.status = status
    
    if status == 'completed':
        task.completed_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # Отправляем сообщение в зависимости от роли
        if task.assignee_id == current_user.id:
            flash('Статус задачи обновлён', 'success')
        else:
            flash('Статус задачи обновлён', 'success')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка: {str(e)}', 'danger')
    
    return redirect(url_for('project.view', project_id=task.project_id))

@project_bp.route('/task/<int:task_id>/add-report', methods=['GET', 'POST'])
@login_required
def add_task_report(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Только исполнитель может добавлять отчёт
    if task.assignee_id != current_user.id:
        flash('Только исполнитель может добавлять отчёт к задаче', 'danger')
        return redirect(url_for('project.view', project_id=task.project_id))
    
    if request.method == 'POST':
        report_text = request.form.get('report_text')
        files = request.files.getlist('report_files')
        
        # Сохраняем файлы
        saved_files = None
        if files and files[0].filename:
            saved_files = save_task_files(files, task_id)

        task.report_text = report_text
        if saved_files:
            task.report_files = saved_files
        
        # Если задача ещё не завершена и добавлен отчёт, можно предложить завершить
        if task.status != 'completed':
            task.status = 'in_progress'
        
        try:
            db.session.commit()
            flash('Отчёт добавлен успешно', 'success')
            return redirect(url_for('project.view', project_id=task.project_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'danger')
    
    return render_template('projects/add_task_report.html', task=task)

@project_bp.route('/task/<int:task_id>/report-data')
@login_required
def get_task_report_data(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Проверка доступа
    if current_user.role.name != 'director' and task.project.manager_id != current_user.id and task.assignee_id != current_user.id:
        return jsonify({'error': 'Нет доступа'}), 403
    
    import json
    files = []
    if task.report_files:
        try:
            files = json.loads(task.report_files)
        except:
            files = []
    
    return jsonify({
        'title': task.title,
        'report_text': task.report_text or 'Нет текстового отчёта',
        'report_files': files,
        'status': task.status,
        'completed_at': task.completed_at.strftime('%d.%m.%Y %H:%M') if task.completed_at else None
    })