from datetime import datetime
from ..extensions import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_employee(employee_id):
    return Employee.query.get(int(employee_id))

class Employee(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    patronymic = db.Column(db.String(50))
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200))
    phone = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(100), unique=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='SET NULL'), nullable=True)
    avatar = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    role = db.relationship('Role', backref='employees')
    salaries = db.relationship('Salary', backref='employee', cascade='all, delete-orphan')