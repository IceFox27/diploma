from datetime import datetime
from ..extensions import db

# --- ВСПОМОГАТЕЛЬНАЯ ТАБЛИЦА ДЛЯ СВЯЗИ "МНОГИЕ КО МНОГИМ" ---
# ДОЛЖНА БЫТЬ ОПРЕДЕЛЕНА ДО МОДЕЛИ PROJECT
project_workers = db.Table('project_workers',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), primary_key=True),
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.id', ondelete='CASCADE'), primary_key=True),
    db.Column('assigned_at', db.DateTime, default=datetime.utcnow),
    db.Column('assigned_by_id', db.Integer, db.ForeignKey('employee.id'))
)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='planning')
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    actual_start_date = db.Column(db.Date)
    actual_end_date = db.Column(db.Date)
    budget = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    actual_cost = db.Column(db.Numeric(12, 2), default=0)

    director_id = db.Column(db.Integer, db.ForeignKey('employee.id', ondelete='SET NULL'))
    manager_id = db.Column(db.Integer, db.ForeignKey('employee.id', ondelete='SET NULL'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('employee.id'))

    priority = db.Column(db.String(10), default='medium')
    progress_percent = db.Column(db.Integer, default=0)
    
    # Системные поля
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- Связи ---
    director = db.relationship('Employee', foreign_keys=[director_id], backref='directed_projects')
    manager = db.relationship('Employee', foreign_keys=[manager_id], backref='managed_projects')
    created_by = db.relationship('Employee', foreign_keys=[created_by_id])
    
    # ИСПРАВЛЕННАЯ СВЯЗЬ "многие ко многим"
    # Явно указываем foreign_keys для secondary таблицы
    workers = db.relationship(
        'Employee', 
        secondary='project_workers',
        primaryjoin="Project.id == project_workers.c.project_id",
        secondaryjoin="Employee.id == project_workers.c.employee_id",
        backref=db.backref('assigned_projects', lazy='dynamic'),  # Теперь assigned_projects будет динамическим
        lazy='dynamic'
    )
    
    def __repr__(self):
        return f'<Project {self.name}>'
    
    @property
    def budget_remaining(self):
        """Оставшийся бюджет"""
        if self.actual_cost:
            return self.budget - self.actual_cost
        return self.budget
    
    @property
    def is_over_budget(self):
        """Превышен ли бюджет"""
        return self.actual_cost and self.actual_cost > self.budget
    
    @property
    def is_completed(self):
        """Завершён ли проект"""
        return self.status == 'completed'
    
    @property
    def workers_count(self):
        """Количество сотрудников в проекте"""
        return self.workers.count()
    
    @property
    def tasks_count(self):
        """Количество задач в проекте (если есть модель Task)"""
        from ..models.task import Task
        return Task.query.filter_by(project_id=self.id).count()
    
    def update_progress(self):
        """Обновить процент выполнения проекта"""
        # Если есть задачи, прогресс считается из них
        from ..models.task import Task
        tasks = Task.query.filter_by(project_id=self.id).filter(Task.status != 'cancelled').all()
        if tasks:
            total_progress = sum(t.progress_percent for t in tasks)
            self.progress_percent = total_progress // len(tasks)
        elif self.status == 'completed':
            self.progress_percent = 100
        elif self.status == 'planning':
            self.progress_percent = 10
        elif self.status == 'in_progress':
            self.progress_percent = max(10, min(95, self.progress_percent))
        elif self.status == 'cancelled':
            self.progress_percent = 0
            
        db.session.commit()