# app/routes/categories.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Category, Transaction
from app import db

bp = Blueprint('categories', __name__, url_prefix='/categories')


@bp.route('/')
@login_required
def list_categories():
    """Список всех категорий"""
    categories = current_user.categories.order_by(Category.operation_type, Category.name).all()
    
    # Получаем статистику по категориям
    categories_with_stats = []
    for category in categories:
        transactions_count = category.transactions.count()
        total_amount = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.category_id == category.id
        ).scalar() or 0
        
        categories_with_stats.append({
            'category': category,
            'transactions_count': transactions_count,
            'total_amount': float(total_amount)
        })
    
    return render_template('categories/list.html',
                         categories=categories_with_stats)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_category():
    """Добавление новой категории"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        operation_type = request.form.get('operation_type')
        
        # Валидация
        if not name:
            flash('Введите название категории', 'error')
            return render_template('categories/add.html')
        
        if not operation_type or operation_type not in ['INCOME', 'EXPENSE']:
            flash('Выберите тип категории', 'error')
            return render_template('categories/add.html')
        
        # Проверяем уникальность названия для пользователя
        existing_category = Category.query.filter_by(
            name=name, 
            user_id=current_user.id
        ).first()
        
        if existing_category:
            flash('Категория с таким названием уже существует', 'error')
            return render_template('categories/add.html')
        
        # Создаем категорию
        category = Category(
            name=name,
            operation_type=operation_type,
            user_id=current_user.id
        )
        
        # Сохраняем в БД
        db.session.add(category)
        db.session.commit()
        
        flash('Категория успешно создана!', 'success')
        return redirect(url_for('categories.list_categories'))
    
    return render_template('categories/add.html')

@bp.route('/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    """Редактирование категории"""
    category = Category.query.filter_by(
        id=category_id, 
        user_id=current_user.id
    ).first_or_404()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        operation_type = request.form.get('operation_type')
        
        # Валидация
        errors = []
        if not name:
            errors.append('Введите название категории')
        
        if not operation_type or operation_type not in ['INCOME', 'EXPENSE']:
            errors.append('Выберите тип категории')
        
        # Проверяем уникальность названия (исключая текущую категорию)
        if name and Category.query.filter(
            Category.name == name,
            Category.user_id == current_user.id,
            Category.id != category_id
        ).first():
            errors.append('Категория с таким названием уже существует')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('categories/edit.html', category=category)
        
        try:
            # Обновляем категорию
            category.name = name
            category.operation_type = operation_type
            
            db.session.commit()
            flash('Категория успешно обновлена!', 'success')
            return redirect(url_for('categories.list_categories'))
            
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при обновлении категории', 'error')
            # Логирование ошибки для отладки
            # current_app.logger.error(f'Error updating category: {str(e)}')
    
    return render_template('categories/edit.html', category=category)

@bp.route('/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    """Удаление категории"""
    category = Category.query.filter_by(
        id=category_id, 
        user_id=current_user.id
    ).first_or_404()
    
    # Проверяем, есть ли связанные транзакции
    transactions_count = category.transactions.count()
    
    if transactions_count > 0:
        flash(f'Невозможно удалить категорию. С ней связано {transactions_count} транзакций.', 'error')
        return redirect(url_for('categories.list_categories'))
    
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Категория успешно удалена!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении категории', 'error')
    
    return redirect(url_for('categories.list_categories'))

@bp.route('/<int:category_id>/transactions')
@login_required
def category_transactions(category_id):
    """Просмотр транзакций в категории"""
    category = Category.query.filter_by(
        id=category_id, 
        user_id=current_user.id
    ).first_or_404()
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Получаем транзакции с пагинацией
    transactions = category.transactions.order_by(
        Transaction.date.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    # Вычисляем общую сумму транзакций в категории
    total_amount = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.category_id == category_id,
        Transaction.user_id == current_user.id
    ).scalar() or 0
    
    # Русские названия для типов операций
    operation_type_names = {
        'INCOME': 'Доход',
        'EXPENSE': 'Расход'
    }
    
    return render_template('categories/transactions.html',
                         category=category,
                         transactions=transactions,
                         total_amount=total_amount,
                         operation_type_names=operation_type_names)
    
# API для получения категорий по типу
@bp.route('/api/by-type/<operation_type>')
@login_required
def get_categories_by_type(operation_type):
    """API для получения категорий по типу операции"""
    if operation_type not in ['INCOME', 'EXPENSE']:
        return jsonify({'error': 'Invalid operation type'}), 400
    
    categories = current_user.categories.filter_by(
        operation_type=operation_type
    ).order_by(Category.name).all()
    
    categories_data = [{
        'id': cat.id,
        'name': cat.name,
        'operation_type': cat.operation_type
    } for cat in categories]
    
    return jsonify(categories_data)