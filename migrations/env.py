# migrations/env.py
import logging
from logging.config import fileConfig
import os
import sys

# Добавляем корневую директорию проекта в Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from flask import current_app
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def get_metadata():
    """
    Получаем метаданные из Flask приложения.
    Эта функция гарантирует, что все модели зарегистрированы.
    """
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Импортируем все модели чтобы они зарегистрировались в метаданных
            from app.models.user import User
            from app.models.category import Category
            from app.models.transaction import Transaction

            
            return current_app.extensions['migrate'].db.metadata
    except Exception as e:
        logger.error(f"Error getting metadata: {e}")
        raise


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
            context.configure(
                url=url,
                target_metadata=get_metadata(),
                literal_binds=True,
                dialect_opts={"paramstyle": "named"},
            )
    except Exception:
        # Fallback to alembic.ini configuration
        url = config.get_main_option("sqlalchemy.url")
        context.configure(
            url=url,
            target_metadata=get_metadata(),
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    from app import create_app
    app = create_app()

    # Подключаемся к базе данных через Flask-SQLAlchemy
    with app.app_context():
        connectable = current_app.extensions['migrate'].db.engine

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=get_metadata(),
                compare_type=True,          # Сравнивать типы колонок
                compare_server_default=True, # Сравнивать значения по умолчанию
            )

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()