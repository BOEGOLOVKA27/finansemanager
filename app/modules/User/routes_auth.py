from . import *


bp = bp_auth

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

        print(user)
        print(user.password)
        print(password)
        print(check_password_hash(user.password, password))
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            flash('Успешная авторизация!', 'success')
            return redirect(url_for('main.index'))  # ← Изменено на главную страницу финансов
        else:
            flash('Неверный логин или пароль!', 'danger')
            return redirect(url_for('auth.login'))
        
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



@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Генерируем токен сброса пароля
            reset_token = secrets.token_urlsafe(32)
            user.reset_token = reset_token
            user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # Отправляем email
            if send_password_reset_email(user.email, reset_token):
                flash('На вашу почту отправлена ссылка для сброса пароля. Ссылка действительна 1 час.', 'info')
            else:
                flash('Ошибка при отправке email. Попробуйте позже.', 'danger')
        else:
            # Для безопасности показываем одинаковое сообщение
            flash('Если email зарегистрирован, на него будет отправлена ссылка для сброса пароля.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Проверяем токен
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        flash('Ссылка для сброса пароля недействительна или устарела.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Обновляем пароль
        user.password = generate_password_hash(form.password.data)
        user.reset_token = None  # Удаляем токен после использования
        user.reset_token_expires = None
        db.session.commit()
        
        flash('Пароль успешно изменен! Теперь вы можете войти с новым паролем.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form, token=token)

def send_password_reset_email(email, token):
    """Отправка email для сброса пароля"""
    try:
        msg = Message('Сброс пароля - FinanceTrack', 
                     sender=current_app.config['MAIL_USERNAME'], 
                     recipients=[email])
        
        reset_link = url_for('auth.reset_password', token=token, _external=True)
        
        msg.body = f"""
        Здравствуйте,

        Вы запросили сброс пароля для вашего аккаунта в Финансовом трекере.

        Для сброса пароля перейдите по ссылке:
        {reset_link}

        Если вы не запрашивали сброс пароля, проигнорируйте это письмо.

        Ссылка действительна в течение 1 часа.

        С наилучшими пожеланиями,
        Команда Финансового трекера
        """
        
        msg.html = f"""
        <h3>Сброс пароля - FinanceTrack</h3>
        <p>Здравствуйте,</p>
        <p>Вы запросили сброс пароля для вашего аккаунта.</p>
        <p><a href="{reset_link}">Нажмите здесь для сброса пароля</a></p>
        <p>Если вы не запрашивали сброс пароля, проигнорируйте это письмо.</p>
        <p><em>Ссылка действительна в течение 1 часа.</em></p>
        <br>
        <p>С наилучшими пожеланиями,<br>Команда Финансового трекера</p>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Ошибка отправки email для сброса пароля: {e}")
        return False