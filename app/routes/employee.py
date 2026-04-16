from datetime import datetime
from flask import Blueprint, render_template, redirect, flash, url_for, request
from flask_login import login_user, logout_user

from ..functions import save_picture
from ..forms import RegistrationForm, LoginForm
from ..extensions import db, bcrypt
from ..models.employee import Employee
from ..models.role import Role

employee = Blueprint('employee', __name__)

@employee.route('/employee/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        avatar_filename = save_picture(form.avatar.data)
        
        # Создаем сотрудника с выбранной ролью (убираем поиск роли по умолчанию)
        employee = Employee(
            last_name=form.last_name.data,
            first_name=form.first_name.data,
            patronymic=form.patronymic.data,
            login=form.login.data,
            password=hashed_password,
            phone=form.phone.data,
            email=form.email.data,
            avatar=avatar_filename,
            role_id=form.role.data  # Используем выбранную роль из формы
        )
        
        try:
            db.session.add(employee)
            db.session.commit()
            flash(f"{form.login.data} успешно зарегистрирован", "success")
            return redirect(url_for('employee.login')) 
        except Exception as e:
            print(str(e))
            flash(f"При регистрации сотрудника произошла ошибка", "danger")
    return render_template('employee/register.html', form=form)

@employee.route('/employee/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        employee = Employee.query.filter_by(login=form.login.data).first()
        if employee and bcrypt.check_password_hash(employee.password, form.password.data):
            # Обновляем время последнего захода
            employee.last_seen = datetime.utcnow()
            db.session.commit()
            
            login_user(employee, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f"Поздравляем, {employee.first_name} {employee.last_name}! Вы успешно авторизованы", "success")
            return redirect(next_page) if next_page else redirect(url_for('main.index'))  # исправил post.all на main.index
        else:
            flash(f"Ошибка входа. Пожалуйста проверьте логин и пароль!", "danger")

    return render_template('employee/login.html', form=form)

@employee.route('/employee/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('main.index'))  # исправил index.html на main.index