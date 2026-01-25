# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from config import config
from flask_wtf.csrf import CSRFProtect
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate 
from flask_jwt_extended import JWTManager


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
ma = Marshmallow() 
jwt = JWTManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """
        Колбэк для загрузки пользователя из JWT токена
        """
        identity = jwt_data["sub"]  # Получаем identity из токена
        
        # У вас identity = f'{user.id}' (строка), конвертируем в int
        try:
            user_id = int(identity)  # Преобразуем строку '5' в число 5
            return User.query.get(user_id)  # Находим пользователя в БД
        except (ValueError, TypeError):
            return None

    # Настройка Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
    login_manager.login_message_category = 'info'
    
    # Регистрация загрузчика пользователя
    from app.modules.User.models  import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Регистрация blueprint'ов
    register_blueprints(app)
    
    register_context_processors(app)
    
    return app

def register_blueprints(app):

    
    """Регистрация всех blueprint'ов"""
    from app.routes.main import bp as main_bp
    
    from app.modules.User import bp_auth as auth_bp
    from app.modules.User import bp_profile as profile_bp  
    
    from app.modules.Transaction import bp as transactions_bp

    from app.modules.Categories import bp as categories_bp
    from app.modules import api_bp
    
    # Исключение API blueprint из CSRF защиты
    csrf.exempt(api_bp)
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(profile_bp, url_prefix='/profile') 
    app.register_blueprint(transactions_bp, url_prefix='/transactions')
    app.register_blueprint(categories_bp, url_prefix='/categories')
    app.register_blueprint(api_bp) 


def register_context_processors(app):
    """Регистрация контекстных процессоров Jinja2"""
    from datetime import datetime
    
    @app.context_processor
    def utility_processor():
        def format_currency(amount):
            """Форматирование денежных сумм"""
            if amount is None:
                return "0.00 ₽"
            try:
                # Преобразуем в float и форматируем
                amount_float = float(amount)
                return f"{amount_float:,.2f} ₽".replace(',', ' ')
            except (ValueError, TypeError):
                return "0.00 ₽"
        
        def format_date(date_value, format_string='%d.%m.%Y'):
            """Форматирование дат"""
            if date_value is None:
                return ""
            if isinstance(date_value, str):
                try:
                    date_value = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                except ValueError:
                    return date_value
            return date_value.strftime(format_string)
        
        def format_datetime(datetime_value, format_string='%d.%m.%Y %H:%M'):
            """Форматирование даты и времени"""
            if datetime_value is None:
                return ""
            if isinstance(datetime_value, str):
                try:
                    datetime_value = datetime.fromisoformat(datetime_value.replace('Z', '+00:00'))
                except ValueError:
                    return datetime_value
            return datetime_value.strftime(format_string)
        
        # Все функции будут доступны во всех шаблонах
        return dict(
            format_currency=format_currency,
            format_date=format_date,
            format_datetime=format_datetime,
            now=datetime.now
        )
        
          