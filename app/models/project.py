from datetime import datetime
from ..extensions import db

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
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    director = db.relationship('Employee', foreign_keys=[director_id], backref='directed_projects')
    manager = db.relationship('Employee', foreign_keys=[manager_id], backref='managed_projects')
    created_by = db.relationship('Employee', foreign_keys=[created_by_id])
    
    workers = db.relationship(
        'Employee', 
        secondary='project_workers',
        primaryjoin="Project.id == project_workers.c.project_id",
        secondaryjoin="Employee.id == project_workers.c.employee_id",
        backref=db.backref('assigned_projects', lazy='dynamic'),  
        lazy='dynamic'
    )
    
    def __repr__(self):
        return f'<Project {self.name}>'
    
    @property
    def budget_remaining(self):
        if self.actual_cost:
            return self.budget - self.actual_cost
        return self.budget
    
    @property
    def is_over_budget(self):
        return self.actual_cost and self.actual_cost > self.budget
    
    @property
    def is_completed(self):
        return self.status == 'completed'
    
    @property
    def workers_count(self):
        return self.workers.count()
    
    @property
    def progress_percent_float(self):
        """Процент выполнения (0-1)"""
        if self.progress_percent:
            return self.progress_percent / 100
        return 0

    @property
    def days_spent(self):
        """Сколько дней прошло с начала работ"""
        if not self.actual_start_date:
            return 0
        diff = datetime.utcnow().date() - self.actual_start_date
        return diff.days

    @property
    def days_remaining_planned(self):
        """Плановый остаток дней (по изначальному плану)"""
        if not self.end_date:
            return 0
        diff = self.end_date - datetime.utcnow().date()
        return max(diff.days, 0)

    @property
    def current_speed(self):
        """Текущая скорость выполнения (% в день)"""
        if self.days_spent == 0:
            return 0
        return self.progress_percent_float / self.days_spent

    @property
    def predicted_days_remaining(self):
        """Прогнозируемый остаток дней"""
        if self.current_speed == 0:
            return self.days_remaining_planned
        remaining_work = 1 - self.progress_percent_float
        return int(remaining_work / self.current_speed)

    @property
    def predicted_completion_date(self):
        """Прогнозируемая дата завершения"""
        from datetime import timedelta
        if self.predicted_days_remaining <= 0:
            return self.end_date
        return datetime.utcnow().date() + timedelta(days=self.predicted_days_remaining)

    @property
    def deviation_days(self):
        """Отклонение от плана (в днях)"""
        if not self.end_date:
            return 0
        return self.predicted_days_remaining - self.days_remaining_planned

    @property
    def status_color(self):
        """Цвет статуса для отображения"""
        if self.deviation_days <= 0:
            return 'green'      # идём по графику или с опережением
        elif self.deviation_days <= 14:
            return 'yellow'     # отставание до 14 дней
        else:
            return 'red'        # отставание больше 14 дней