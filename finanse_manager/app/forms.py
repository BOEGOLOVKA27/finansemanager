# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, TextAreaField, SelectField, DateField, DecimalField,RadioField  
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Length, Optional
from app.models.user import User
from datetime import datetime
from flask_login import current_user
from .models import User


# Форма для логина (из вашего кода)
class LoginForm(FlaskForm):
    login = StringField('Логин или Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

# Форма для регистрации (из вашего кода)
class RegistrationForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email(message='Некорректный email адрес'),])
    password = PasswordField('Пароль', validators=[DataRequired()])
    replaypassword = PasswordField('Повторите пароль',
                                   validators=[DataRequired(), EqualTo('password', message='Пароли должны совпадать')])
    submit = SubmitField('Ввод')

class TransactionForm(FlaskForm):
    operation_type = SelectField('Тип операции', 
                                choices=[('INCOME', 'Доход'), ('EXPENSE', 'Расход')],
                                validators=[DataRequired()])
    amount = DecimalField('Сумма', validators=[DataRequired(), NumberRange(min=0.01)])
    description = TextAreaField('Описание')
    category_id = SelectField('Категория', coerce=int, validators=[DataRequired()])
    date = DateField('Дата', default=datetime.utcnow, validators=[DataRequired()])
    operation_type = SelectField('Тип операции', choices=[('INCOME', 'Доход'), ('EXPENSE', 'Расход')])
    submit = SubmitField('Добавить транзакцию')

class CategoryForm(FlaskForm):
    name = StringField('Название категории', validators=[DataRequired()])
    operation_type = SelectField('Тип операции', choices=[
        ('INCOME', 'Доход'),
        ('EXPENSE', 'Расход')
    ], validators=[DataRequired()])
    submit = SubmitField('Создать категорию')
    
    
    
class ChangeLoginForm(FlaskForm):
    new_login = StringField('Новый логин', validators=[
        DataRequired(message='Логин обязателен'),
        Length(min=3, max=64, message='Логин должен быть от 3 до 64 символов')
    ])
    submit = SubmitField('Сменить логин')

    def validate_new_login(self, new_login):
        # Проверяем, что новый логин не совпадает с текущим
        if new_login.data == current_user.login:
            raise ValidationError('Новый логин должен отличаться от текущего')
        
        # Проверяем, что логин не занят другим пользователем
        user = User.query.filter_by(login=new_login.data).first()
        if user and user.id != current_user.id:
            raise ValidationError('Этот логин уже занят')

class ChangeEmailForm(FlaskForm):
    new_email = StringField('Новый email', validators=[
        DataRequired(message='Email обязателен'),
        Email(message='Введите корректный email'),
        Length(max=120, message='Email слишком длинный')
    ])
    submit = SubmitField('Сменить email')

    def validate_new_email(self, new_email):
        # Проверяем, что новый email не совпадает с текущим
        if new_email.data == current_user.email:
            raise ValidationError('Новый email должен отличаться от текущего')
        
        # Проверяем, что email не занят другим пользователем
        user = User.query.filter_by(email=new_email.data).first()
        if user and user.id != current_user.id:
            raise ValidationError('Этот email уже занят')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Текущий пароль', validators=[
        DataRequired(message='Текущий пароль обязателен')
    ])
    new_password = PasswordField('Новый пароль', validators=[
        DataRequired(message='Новый пароль обязателен'),
        Length(min=6, message='Пароль должен содержать минимум 6 символов')
    ])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(message='Подтверждение пароля обязательно'),
        EqualTo('new_password', message='Пароли не совпадают')
    ])
    submit = SubmitField('Сменить пароль')

    def validate_current_password(self, current_password):
        # Проверяем текущий пароль
        if not current_user.check_password(current_password.data):
            raise ValidationError('Текущий пароль введен неверно')

    def validate_new_password(self, new_password):
        # Проверяем, что новый пароль отличается от текущего
        if current_user.check_password(new_password.data):
            raise ValidationError('Новый пароль должен отличаться от текущего')    
        
class TransactionForm(FlaskForm):
    amount = FloatField('Сумма', validators=[
        DataRequired(message='Сумма обязательна'),
        NumberRange(min=0.01, message='Сумма должна быть больше 0')
    ])
    description = TextAreaField('Описание', validators=[
        Optional(),
        Length(max=500, message='Описание слишком длинное')
    ])
    date = DateField('Дата', validators=[
        DataRequired(message='Дата обязательна')
    ], default=datetime.now)
    operation_type = RadioField('Тип операции', choices=[
        ('INCOME', 'Доход'),
        ('EXPENSE', 'Расход')
    ], validators=[
        DataRequired(message='Выберите тип операции')
    ], default='EXPENSE')
    category_id = SelectField('Категория', coerce=int, validators=[
        DataRequired(message='Выберите категорию')
    ])        