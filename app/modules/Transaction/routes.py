from . import *
from ..Categories.models import Category
from flask import current_app

@bp.route('/')
@login_required
def list_transactions():
    """Список всех транзакций"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Получаем транзакции с пагинацией
    transactions = current_user.transactions.order_by(
        Transaction.date.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    # Получаем все категории для фильтров
    categories = current_user.categories.all()
    
    return render_template('transactions/list.html',
                         transactions=transactions,
                         categories=categories)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    """Добавление новой транзакции"""
    # Получаем категории пользователя
    categories = current_user.categories.all()
    
    # Популярные категории для быстрого выбора
    popular_categories = [
        {'name': 'Зарплата', 'operation_type': 'INCOME', 'icon': 'fa-briefcase'},
        {'name': 'Продукты', 'operation_type': 'EXPENSE', 'icon': 'fa-shopping-cart'},
        {'name': 'Транспорт', 'operation_type': 'EXPENSE', 'icon': 'fa-car'},
        {'name': 'Развлечения', 'operation_type': 'EXPENSE', 'icon': 'fa-film'},
        {'name': 'Здоровье', 'operation_type': 'EXPENSE', 'icon': 'fa-heart'},
    ]
    
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            amount_str = request.form.get('amount', '0').replace(' ', '').replace(',', '.')
            amount = float(amount_str)
            description = request.form.get('description', '').strip()
            operation_type = request.form.get('operation_type')
            category_id = request.form.get('category_id')
            date_str = request.form.get('date')
            
            # Валидация
            if not amount or amount <= 0:
                flash('Сумма должна быть положительным числом', 'error')
                return render_template('transactions/add.html', 
                                     categories=categories,
                                     popular_categories=popular_categories,
                                     default_date=datetime.utcnow().strftime('%Y-%m-%d'))
            
            if not operation_type or operation_type not in ['INCOME', 'EXPENSE']:
                flash('Выберите тип операции', 'error')
                return render_template('transactions/add.html',
                                     categories=categories,
                                     popular_categories=popular_categories,
                                     default_date=datetime.utcnow().strftime('%Y-%m-%d'))
            
            if not category_id:
                flash('Выберите категорию', 'error')
                return render_template('transactions/add.html',
                                     categories=categories,
                                     popular_categories=popular_categories,
                                     default_date=datetime.utcnow().strftime('%Y-%m-%d'))
            
            # Проверяем существование категории
            category = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
            if not category:
                flash('Выбранная категория не найдена', 'error')
                return render_template('transactions/add.html',
                                     categories=categories,
                                     popular_categories=popular_categories,
                                     default_date=datetime.utcnow().strftime('%Y-%m-%d'))
            
            # Проверяем соответствие типа операции категории
            if category.operation_type != operation_type:
                flash('Тип операции не соответствует выбранной категории', 'error')
                return render_template('transactions/add.html',
                                     categories=categories,
                                     popular_categories=popular_categories,
                                     default_date=datetime.utcnow().strftime('%Y-%m-%d'))
            
            # Парсим дату
            if date_str:
                transaction_date = datetime.strptime(date_str, '%Y-%m-%d')
            else:
                transaction_date = datetime.utcnow()
            
            # Создаем транзакцию
            transaction = Transaction(
                amount=amount,
                description=description,
                operation_type=operation_type,
                category_id=category_id,
                user_id=current_user.id,
                date=transaction_date
            )
            
            # Сохраняем в БД
            db.session.add(transaction)
            db.session.commit()
            
            flash('Транзакция успешно добавлена!', 'success')
            return redirect(url_for('transactions.list_transactions'))
            
        except ValueError:
            flash('Некорректный формат суммы', 'error')
            return render_template('transactions/add.html',
                                 categories=categories,
                                 popular_categories=popular_categories,
                                 default_date=datetime.utcnow().strftime('%Y-%m-%d'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при добавлении транзакции', 'error')
            current_app.logger.error(f'Error adding transaction: {str(e)}')
    
    # Для GET запроса - текущая дата по умолчанию
    default_date = datetime.utcnow().strftime('%Y-%m-%d')
    return render_template('transactions/add.html',
                         categories=categories,
                         popular_categories=popular_categories,
                         default_date=default_date)

@bp.route('/<int:transaction_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    """Редактирование транзакции"""
    transaction = Transaction.query.filter_by(
        id=transaction_id, 
        user_id=current_user.id
    ).first_or_404()
    
    categories = current_user.categories.all()
    
    if request.method == 'POST':
        amount_str = request.form.get('amount', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id')
        date_str = request.form.get('date')
        
        # Валидация
        errors = []
        
        # Валидация суммы
        try:
            amount = float(amount_str) if amount_str else 0
            if amount <= 0:
                errors.append('Сумма должна быть положительным числом')
        except (ValueError, TypeError):
            errors.append('Некорректный формат суммы')
        
        # Валидация категории
        if not category_id:
            errors.append('Выберите категорию')
        else:
            category = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
            if not category:
                errors.append('Выбранная категория не найдена')
        
        # Валидация даты
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                errors.append('Некорректный формат даты')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('transactions/edit.html',
                                 transaction=transaction,
                                 categories=categories)
        
        try:
            # Обновляем транзакцию
            transaction.amount = amount
            transaction.description = description
            transaction.category_id = category_id
            transaction.operation_type = category.operation_type  # Синхронизируем с категорией
            
            if date_str:
                transaction.date = datetime.strptime(date_str, '%Y-%m-%d')
            
            db.session.commit()
            
            flash('Транзакция успешно обновлена!', 'success')
            return redirect(url_for('transactions.list_transactions'))
            
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при обновлении транзакции', 'error')
            # Логирование для отладки
            # current_app.logger.error(f'Error updating transaction: {str(e)}')
    
    return render_template('transactions/edit.html',
                         transaction=transaction,
                         categories=categories)

@bp.route('/<int:transaction_id>/delete', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    """Удаление транзакции"""
    transaction = Transaction.query.filter_by(
        id=transaction_id, 
        user_id=current_user.id
    ).first_or_404()
    
    try:
        db.session.delete(transaction)
        db.session.commit()
        flash('Транзакция успешно удалена!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении транзакции', 'error')
    
    return redirect(url_for('transactions.list_transactions'))

@bp.route('/category/create_ajax', methods=['POST'])
@login_required
def create_category_ajax():
    """Создание категории через AJAX"""
    name = request.form.get('name', '').strip()
    operation_type = request.form.get('operation_type')
    
    # Валидация
    errors = []
    if not name:
        errors.append('Введите название категории')
    
    if not operation_type or operation_type not in ['INCOME', 'EXPENSE']:
        errors.append('Выберите тип категории')
    
    # Проверяем уникальность названия
    if name and Category.query.filter(
        Category.name == name,
        Category.user_id == current_user.id
    ).first():
        errors.append('Категория с таким названием уже существует')
    
    if errors:
        return jsonify({'success': False, 'errors': errors})
    
    try:
        category = Category(
            name=name,
            operation_type=operation_type,
            user_id=current_user.id
        )
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name,
                'operation_type': category.operation_type
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'errors': ['Ошибка при создании категории']})