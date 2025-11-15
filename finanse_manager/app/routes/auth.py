# app/routes/auth.py
from flask import (render_template, request, redirect, url_for, flash, 
                   Blueprint, session, current_app)
from werkzeug.security import generate_password_hash
from flask_login import login_user, login_required, current_user, logout_user
import secrets
from app.models.user import User
from app.models.category import Category
from werkzeug.security import check_password_hash
from app.forms import LoginForm, RegistrationForm
from app import db, mail
from flask_mail import Message
from config import config

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username_or_email = form.login.data
        password = form.password.data
        
        # Поиск пользователя по логину или email
        user = User.query.filter(
            (User.login == username_or_email) | (User.email == username_or_email)
        ).first()
        
        login_user(user, remember=True)

        # if user and check_password_hash(user.password, password):
        #     login_user(user, remember=True)
        #     flash('Успешная авторизация!', 'success')
        #     return redirect(url_for('main.index'))  # ← Изменено на главную страницу финансов
        # else:
        #     flash('Неверный логин или пароль!', 'danger')
        #     return redirect(url_for('auth.login'))
        
        return redirect(url_for('main.index'))  

    return render_template('auth/login.html', form=form)
    

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Выход выполнен!', 'success')
    return redirect(url_for('main.index'))  

@bp.route('/signup', methods=['POST', 'GET'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.login.data
        email = form.email.data
        password = form.password.data

        existing_user = User.query.filter_by(login=username).first()
        if existing_user:
            flash('Пользователь с таким именем уже существует', 'error')
            return redirect(url_for('auth.signup'))
        print('тут 1')
        if not send_confirmation_email(email):
            flash('Ошибка в отправке подтверждающего письма', 'error')
            return redirect(url_for('auth.signup'))

        session['data'] = {'username': username, 'email': email, 'password': password}
        flash('На ваш email было отправлено письмо с подтверждением.', 'info')
        return redirect(url_for('auth.signup'))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Ошибка в поле {getattr(form, field).label.text}: {error}", 'danger')

    return render_template('auth/signup.html', form=form)

def send_confirmation_email(email):
    try:
        key = config['default'].serializer.dumps(email, salt='email-confirm')
        msg = Message('Подтверждение Email', 
                     sender=current_app.config['MAIL_USERNAME'], 
                     recipients=[email])
        link = url_for('auth.confirm_email', token=key, _external=True)
        msg.body = f"""
        Здравствуйте,

        Спасибо за регистрацию в Финансовом трекере! Чтобы завершить процесс, пожалуйста, подтвердите ваш адрес электронной почты, перейдя по следующей ссылке:

        {link}

        Если вы не регистрировались на нашем сайте, просто проигнорируйте это сообщение.

        С наилучшими пожеланиями,
        Команда Финансового трекера
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Ошибка отправки email: {e}")
        return False

@bp.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = config['default'].serializer.loads(token, salt='email-confirm', max_age=600)
        print(f'Подтверждение email для: {email}')
    except Exception as e:
        print(e)
        flash('Ссылка подтверждения недействительна или устарела.', 'danger')
        return redirect(url_for('auth.login'))

    data = session.get('data')
    if not data:
        flash('Сессия истекла. Пожалуйста, попробуйте снова.', 'error')
        return redirect(url_for('auth.signup'))

    username = data['username']
    password = data['password']

    hashed_password = generate_password_hash(password)
    user_token = secrets.token_hex(20)[:20]

    new_user = User(email=email, login=username, password=hashed_password, token=user_token)

    if not new_user.add():
        flash('Ошибка создания пользователя. Попробуйте снова.', 'error')
        return redirect(url_for('auth.signup'))
    
    db.session.commit()

    login_user(new_user)
    flash('Вы успешно подтвердили ваш email.', 'success')

    return redirect(url_for('main.index'))  