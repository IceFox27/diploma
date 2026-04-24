from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps

from ..functions import save_picture
from ..forms import RegistrationForm, LoginForm
from ..extensions import db, bcrypt
from ..models.employee import Employee
from ..models.role import Role

employee = Blueprint('employee', __name__)

def director_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('employee.login'))
        if current_user.role.name != 'director':
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@employee.route('/employee/register', methods=['POST', 'GET'])
@login_required
@director_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        avatar_filename = save_picture(form.avatar.data)
        
        employee = Employee(
            last_name=form.last_name.data,
            first_name=form.first_name.data,
            patronymic=form.patronymic.data,
            login=form.login.data,
            password=hashed_password,
            phone=form.phone.data,
            email=form.email.data,
            avatar=avatar_filename,
            role_id=form.role.data  
        )
        
        try:
            db.session.add(employee)
            db.session.commit()
            flash(f"{form.login.data} успешно зарегистрирован", "success")
            return redirect(url_for('work.index'))
        except Exception as e:
            print(str(e))
            flash(f"При регистрации сотрудника произошла ошибка", "danger")
            db.session.rollback()
    
    return render_template('employee/register.html', form=form)

@employee.route('/employee/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        employee = Employee.query.filter_by(login=form.login.data).first()
        
        if employee and bcrypt.check_password_hash(employee.password, form.password.data):
            employee.last_seen = datetime.utcnow()
            db.session.commit()
            login_user(employee, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
    
    return render_template('employee/login.html', form=form)

@employee.route('/employee/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@employee.route('/employee/profile')
@login_required
def profile():
    return render_template('employee/profile.html', employee=current_user)