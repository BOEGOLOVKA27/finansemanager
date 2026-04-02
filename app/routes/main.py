# app/routes/main.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..modules.models import *
from ..modules.Task.models import task_tags
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
    
    # Получаем задачи пользователя
    all_tasks = current_user.tasks.order_by(Task.created_at.desc()).limit(5).all()
    tasks_summary = {
        'total': current_user.tasks.count(),
        'completed': current_user.tasks.filter_by(completed=True).count(),
        'pending': current_user.tasks.filter_by(completed=False).count()
    }
    
    return render_template('index.html',
                        monthly_stats=monthly_stats,
                        total_stats=total_stats,
                        categories_summary=categories_summary,
                        monthly_transactions=monthly_transactions,
                        section_date=section_date,
                        page=page,
                        tasks=all_tasks,
                        tasks_summary=tasks_summary)



@bp.route('/feedback')
def feedback():
    """Страница обратной связи"""
    return render_template('feedback.html')


@bp.route('/tasks')
@login_required
def tasks():
    """Страница управления задачами"""
    return render_template('tasks/tasks.html')