# forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from .models.employee import Employee
from .models.role import Role  # Добавить импорт Role

class RegistrationForm(FlaskForm):
    last_name = StringField('Фамилия', validators=[DataRequired(), Length(min=2, max=50)])
    first_name = StringField('Имя', validators=[DataRequired(), Length(min=2, max=50)])
    patronymic = StringField('Отчество', validators=[Length(max=50)])
    login = StringField('Логин', validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[DataRequired(), Length(min=10, max=20)])
    role = SelectField('Роль', coerce=int, validators=[DataRequired()])  # Добавлено поле role
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтверждение пароля', 
                                   validators=[DataRequired(), EqualTo('password')])
    avatar = FileField('Аватарка', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Зарегистрировать сотрудника')
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Заполняем выбор ролей из базы данных
        self.role.choices = [(role.id, role.display_name) for role in Role.query.all()]
    
    def validate_login(self, login):
        user = Employee.query.filter_by(login=login.data).first()
        if user:
            raise ValidationError('Этот логин уже занят. Пожалуйста, выберите другой.')
    
    def validate_email(self, email):
        user = Employee.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже используется.')
    
    def validate_phone(self, phone):
        user = Employee.query.filter_by(phone=phone.data).first()
        if user:
            raise ValidationError('Этот номер телефона уже используется.')


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')