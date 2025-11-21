# app/models/user.py
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import func, extract
from .transaction import Transaction
from .category import Category

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(128), nullable=False)
    token = db.Column(db.String(20))
    telegram_user_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи с финансовыми данными
    categories = db.relationship('Category', back_populates='user', 
                               cascade='all, delete-orphan', lazy='dynamic')
    transactions = db.relationship('Transaction', back_populates='user',
                                 cascade='all, delete-orphan', lazy='dynamic')
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def change_login(self, new_login):
        """Изменение логина"""
        self.login = new_login
        return self._save()
    
    def change_email(self, new_email):
        """Изменение email"""
        self.email = new_email
        return self._save()
    
    def change_password(self, new_password):
        """Изменение пароля"""
        self.set_password(new_password)
        return self._save()
    
    def _save(self):
        """Внутренний метод для сохранения изменений"""
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    def add(self):
        """Сохранение пользователя в БД"""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False

    # Оптимизированные методы для работы с категориями и транзакциями
    
    def get_categories_by_type(self, operation_type=None):
        """
        Получить категории по типу операции
        """
        query = self.categories
        if operation_type:
            query = query.filter_by(operation_type=operation_type)
        return query.all()
    
    def get_transactions(self, start_date=None, end_date=None, category_id=None, operation_type=None):
        """
        Универсальный метод для получения транзакций с фильтрами
        """
        query = self.transactions
        
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        if category_id:
            query = query.filter_by(category_id=category_id)
        if operation_type:
            query = query.filter_by(operation_type=operation_type)
            
        return query.order_by(Transaction.date.desc()).all()
    
    def get_category_stats(self, days=30):
        """
        Получить статистику по всем категориям за период (оптимизированная версия)
        """
        from sqlalchemy import func, and_
        from datetime import timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Используем SQL запросы вместо Python-фильтрации
        categories_stats = []
        
        for category in self.categories:
            # SQL запрос для статистики по категории
            stats_query = db.session.query(
                func.count(Transaction.id).label('transaction_count'),
                func.sum(Transaction.amount).label('total_amount')
            ).filter(
                and_(
                    Transaction.category_id == category.id,
                    Transaction.date >= start_date,
                    Transaction.date <= end_date
                )
            ).first()
            
            if stats_query.transaction_count and stats_query.transaction_count > 0:
                stats = {
                    'category': category.to_dict(),
                    'transaction_count': stats_query.transaction_count,
                    'total_amount': float(stats_query.total_amount or 0),
                    'average_amount': float((stats_query.total_amount or 0) / stats_query.transaction_count)
                }
                categories_stats.append(stats)
        
        return categories_stats
    
    def get_financial_overview(self, year=None, month=None):
        """
        Получить общий финансовый обзор с группировкой по категориям (оптимизированная версия)
        """
        from sqlalchemy import extract, func
        
        query = self.transactions.join(Category)
        
        if year and month:
            query = query.filter(
                extract('year', Transaction.date) == year,
                extract('month', Transaction.date) == month
            )
        
        # Группируем по категориям с помощью SQL
        result = query.with_entities(
            Category.id,
            Category.name,
            func.count(Transaction.id).label('transaction_count'),
            func.sum(Transaction.amount).label('total_amount')
        ).group_by(Category.id, Category.name).all()
        
        categories_data = []
        for category_id, category_name, count, total in result:
            categories_data.append({
                'category': {
                    'id': category_id,
                    'name': category_name
                },
                'transaction_count': count,
                'total_amount': float(total or 0)
            })
        
        return categories_data
    
    def get_balance_stats(self, year=None, month=None):
        """
        Получить баланс и статистику доходов/расходов (оптимизированная версия)
        """
        from sqlalchemy import func, extract
        
        query = self.transactions
        
        if year and month:
            query = query.filter(
                extract('year', Transaction.date) == year,
                extract('month', Transaction.date) == month
            )
        
        stats = query.with_entities(
            Transaction.operation_type,
            func.sum(Transaction.amount).label('amount'),
            func.count(Transaction.id).label('count')
        ).group_by(Transaction.operation_type).all()
        
        income = 0
        expenses = 0
        total_count = 0
        
        for operation_type, amount, count in stats:
            total_count += count
            if operation_type == 'INCOME':
                income = float(amount or 0)
            else:
                expenses = float(amount or 0)
        
        return {
            "income": income,
            "expenses": expenses,
            "balance": income - expenses,
            "transaction_count": total_count
        }
    
    def get_recent_activity(self, limit=10):
        """
        Получить последние транзакции (для дашборда)
        """
        transactions = self.transactions.join(Category).order_by(
            Transaction.date.desc()
        ).limit(limit).all()
        return [t.to_dict() for t in transactions]
    
    def to_dict(self, include_stats=False):
        """
        Сериализация пользователя с опциональной статистикой
        """
        data = {
            'id': self.id,
            'login': self.login,
            'email': self.email,
            'telegram_user_id': self.telegram_user_id,
            'created_at': self.created_at.isoformat(),
            'categories_count': self.categories.count(),
            'transactions_count': self.transactions.count()
        }
        
        if include_stats:
            data.update(self.get_balance_stats())
            
        return data
    
    def __repr__(self):
        return f'<User {self.login}>'

