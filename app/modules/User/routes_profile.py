from . import *


bp = bp_profile


@bp.route('/')
@login_required
def profile():
    login_form = ChangeLoginForm()
    email_form = ChangeEmailForm()
    password_form = ChangePasswordForm()
    
    return render_template('profile/profile.html', 
                         login_form=login_form,
                         email_form=email_form,
                         password_form=password_form)

@bp.route('/change_login', methods=['POST'])
@login_required
def change_login():
    form = ChangeLoginForm()
    if form.validate_on_submit():
        if current_user.change_login(form.new_login.data):
            flash('Ваш логин успешно изменен.', 'success')
        else:
            flash('Ошибка при изменении логина', 'danger')
    else:
        # Показываем ошибки валидации
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'danger')
    
    return redirect(url_for('profile.profile'))

@bp.route('/change_email', methods=['POST'])
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.change_email(form.new_email.data):
            flash('Ваш email успешно изменен.', 'success')
        else:
            flash('Ошибка при изменении email', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'danger')
    
    return redirect(url_for('profile.profile'))

@bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.change_password(form.new_password.data):
            logout_user()
            flash('Пароль изменен. Пожалуйста, войдите снова', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Ошибка при изменении пароля', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'danger')
    
    return redirect(url_for('profile.profile'))


@bp.route('/add_telegram/<int:user_id>')
@login_required
def add_telegram(user_id):
    if current_user.telegram_user_id is None:
        try:
            current_user.telegram_user_id = user_id
            db.session.commit()
            flash('Ваш Telegram аккаунт успешно привязан.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при привязке Telegram аккаунта: {str(e)}', 'danger')
    else:
        flash('У вас уже есть привязанный Telegram аккаунт.', 'warning')

    return redirect(url_for('profile.profile'))

@bp.route('/unlink_telegram')
@login_required
def unlink_telegram():
    current_user.telegram_user_id = None
    db.session.commit()
    flash('Ваш Telegram аккаунт отвязан.', 'success')
    return redirect(url_for('profile.profile'))