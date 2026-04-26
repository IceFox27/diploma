from datetime import datetime
from ..extensions import db

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='pending')
    priority = db.Column(db.String(10), default='medium')
    
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)
    assigner_id = db.Column(db.Integer, db.ForeignKey('employee.id', ondelete='SET NULL'))  # Кто назначил (менеджер)
    assignee_id = db.Column(db.Integer, db.ForeignKey('employee.id', ondelete='SET NULL'))  # Исполнитель
    
    deadline = db.Column(db.Date)
    completed_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    project = db.relationship('Project', backref=db.backref('tasks', cascade='all, delete-orphan'))
    assigner = db.relationship('Employee', foreign_keys=[assigner_id], backref='assigned_tasks')
    assignee = db.relationship('Employee', foreign_keys=[assignee_id], backref='my_tasks')
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
    @property
    def is_overdue(self):
        if self.deadline and self.status != 'completed':
            return datetime.utcnow().date() > self.deadline
        return False
    
    @property
    def is_completed(self):
        return self.status == 'completed'
    
    @property
    def is_in_progress(self):
        return self.status == 'in_progress'
    
    @property
    def is_pending(self):
        return self.status == 'pending'