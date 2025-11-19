import os
from datetime import timedelta
from itsdangerous import URLSafeSerializer
from dotenv import load_dotenv 

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    WTF_CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT', 465)
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    SCHEDULER_API_ENABLED = True
    
    # Сериализатор для email подтверждения
    serializer = URLSafeSerializer(SECRET_KEY)


class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://admin:111111@localhost/finance_tracker'


config = {
    'default': DevelopmentConfig
}