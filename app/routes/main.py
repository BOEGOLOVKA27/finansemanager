# app/routes/main.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Transaction, Category
from app import db
from sqlalchemy import func, case
from datetime import datetime


bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/page/<int:page>')
def index(page=1):
    """Главная страница"""
    if not current_user.is_authenticated:
        return render_template('index.html')

    month = [
        'Январь', 'Февраль', 'Март',
        'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь',
        'Октябрь', 'Ноябрь', 'Декабрь'
    ]

    now = datetime.now()
    
    section_date = f'{month[now.month - 1]} {now.year}'
    
    # Получаем базовую статистику
    monthly_stats = current_user.get_balance_stats(now.year, now.month)
    total_stats = current_user.get_balance_stats()
    
    # Получаем транзакции с пагинацией
    monthly_transactions = current_user.get_recent_activity_paginated(
        page=page, 
        per_page=5,
        year=now.year,
        month=now.month
    )
    
    # Получаем категории с транзакциями за текущий месяц для диаграмм
    categories = current_user.categories.all()
    
    # Создаем данные для диаграмм
    categories_summary = []
    
    for category in categories:
        # Получаем транзакции этой категории за текущий месяц
        category_transactions = [
            t for t in category.transactions 
            if t.date.year == now.year and t.date.month == now.month
        ]
        
        if category_transactions:
            total_amount = sum(t.amount for t in category_transactions)
            categories_summary.append({
                'category': {
                    'id': category.id,
                    'name': category.name,
                    'operation_type': category.operation_type
                },
                'total_amount': float(total_amount),
                'transaction_count': len(category_transactions)
            })
    
    return render_template('index.html',
                        monthly_stats=monthly_stats,
                        total_stats=total_stats,
                        categories_summary=categories_summary,
                        monthly_transactions=monthly_transactions,
                        section_date=section_date,
                        page=page)



@bp.route('/feedback')
def feedback():
    """Страница обратной связи"""
    return render_template('feedback.html')