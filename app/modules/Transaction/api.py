from datetime import datetime
from flask import jsonify, request
from flask_login import login_required, current_user
from . import *


@api_bp.route('/transactions', methods=['GET'])
@login_required
def get_transactions():
    """Получить все транзакции пользователя"""
    # Базовый запрос
    query = Transaction.query.filter_by(user_id=current_user.id)
    
    # Фильтрация по категории (опционально)
    category_id = request.args.get('category_id', type=int)
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # Фильтрация по типу операции (опционально)
    operation_type = request.args.get('operation_type')
    if operation_type in ['INCOME', 'EXPENSE']:
        query = query.filter_by(operation_type=operation_type)
    
    # Фильтрация по дате (опционально)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date:
        try:
            start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Transaction.date >= start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Transaction.date <= end_date_obj)
        except ValueError:
            pass
    
    # Сортировка по дате (новые сначала)
    query = query.order_by(Transaction.date.desc())
    
    # Пагинация (опционально)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    transactions = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'status': 'success',
        'data': [transaction.to_dict() for transaction in transactions.items],
        'pagination': {
            'page': transactions.page,
            'per_page': transactions.per_page,
            'total': transactions.total,
            'pages': transactions.pages
        }
    })

@api_bp.route('/transactions/<int:transaction_id>', methods=['GET'])
@login_required
def get_transaction(transaction_id):
    """Получить одну транзакцию"""
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=current_user.id
    ).first()
    
    if not transaction:
        return jsonify({'status': 'error', 'message': 'Транзакция не найдена'}), 404
    
    return jsonify({
        'status': 'success',
        'data': transaction.to_dict()
    })

@api_bp.route('/transactions', methods=['POST'])
@login_required
def create_transaction():
    """Создать новую транзакцию"""
    data = request.get_json()
    
    # Валидация обязательных полей
    required_fields = ['amount', 'category_id', 'operation_type']
    for field in required_fields:
        if field not in data or data[field] is None:
            return jsonify({
                'status': 'error', 
                'message': f'Необходимо указать поле {field}'
            }), 400
    
    # Проверка типа операции
    if data['operation_type'] not in ['INCOME', 'EXPENSE']:
        return jsonify({
            'status': 'error', 
            'message': 'operation_type должен быть INCOME или EXPENSE'
        }), 400
    
    # Проверка существования категории и принадлежности пользователю
    category = Category.query.filter_by(
        id=data['category_id'],
        user_id=current_user.id
    ).first()
    
    if not category:
        return jsonify({
            'status': 'error', 
            'message': 'Категория не найдена или у вас нет доступа к ней'
        }), 404
    
    # Проверка соответствия типа операции категории
    if category.operation_type != data['operation_type']:
        return jsonify({
            'status': 'error', 
            'message': f'Тип операции транзакции ({data["operation_type"]}) не соответствует типу категории ({category.operation_type})'
        }), 400
    
    # Проверка даты (если указана)
    date_obj = None
    if data.get('date'):
        try:
            date_obj = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'status': 'error', 
                'message': 'Некорректный формат даты. Используйте ISO формат (YYYY-MM-DDTHH:MM:SS)'
            }), 400
    
    # Создание транзакции
    transaction = Transaction(
        amount=float(data['amount']),
        description=data.get('description', ''),
        operation_type=data['operation_type'],
        category_id=data['category_id'],
        user_id=current_user.id,
        date=date_obj if date_obj else datetime.utcnow()
    )
    
    try:
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': transaction.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error', 
            'message': f'Ошибка при создании транзакции: {str(e)}'
        }), 500

@api_bp.route('/transactions/<int:transaction_id>', methods=['PUT'])
@login_required
def update_transaction(transaction_id):
    """Обновить транзакцию"""
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=current_user.id
    ).first()
    
    if not transaction:
        return jsonify({'status': 'error', 'message': 'Транзакция не найдена'}), 404
    
    data = request.get_json()
    
    # Обновление полей
    if 'amount' in data:
        try:
            transaction.amount = float(data['amount'])
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Некорректная сумма'}), 400
    
    if 'description' in data:
        transaction.description = data['description']
    
    if 'operation_type' in data:
        if data['operation_type'] not in ['INCOME', 'EXPENSE']:
            return jsonify({'status': 'error', 'message': 'Некорректный тип операции'}), 400
        transaction.operation_type = data['operation_type']
    
    if 'category_id' in data:
        # Проверка новой категории
        new_category = Category.query.filter_by(
            id=data['category_id'],
            user_id=current_user.id
        ).first()
        
        if not new_category:
            return jsonify({'status': 'error', 'message': 'Категория не найдена'}), 404
        
        # Проверка соответствия типа операции
        if 'operation_type' in data:
            if new_category.operation_type != data['operation_type']:
                return jsonify({
                    'status': 'error', 
                    'message': f'Тип операции транзакции ({data["operation_type"]}) не соответствует типу новой категории ({new_category.operation_type})'
                }), 400
        else:
            if new_category.operation_type != transaction.operation_type:
                return jsonify({
                    'status': 'error', 
                    'message': f'Тип операции транзакции ({transaction.operation_type}) не соответствует типу новой категории ({new_category.operation_type})'
                }), 400
        
        transaction.category_id = data['category_id']
    
    if 'date' in data:
        try:
            date_obj = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
            transaction.date = date_obj
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Некорректный формат даты'}), 400
    
    try:
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': transaction.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error', 
            'message': f'Ошибка при обновлении транзакции: {str(e)}'
        }), 500

@api_bp.route('/transactions/<int:transaction_id>', methods=['DELETE'])
@login_required
def delete_transaction(transaction_id):
    """Удалить транзакцию"""
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=current_user.id
    ).first()
    
    if not transaction:
        return jsonify({'status': 'error', 'message': 'Транзакция не найдена'}), 404
    
    try:
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Транзакция удалена'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error', 
            'message': f'Ошибка при удалении транзакции: {str(e)}'
        }), 500

@api_bp.route('/transactions/summary', methods=['GET'])
@login_required
def get_transactions_summary():
    """Получить сводку по транзакциям (доходы/расходы за период)"""
    # Параметры фильтрации
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Базовый запрос
    query = Transaction.query.filter_by(user_id=current_user.id)
    
    # Применяем фильтры по дате
    if start_date:
        try:
            start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Transaction.date >= start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Transaction.date <= end_date_obj)
        except ValueError:
            pass
    
    # Получаем все транзакции за период
    transactions = query.all()
    
    # Вычисляем суммы
    total_income = sum(t.amount for t in transactions if t.operation_type == 'INCOME')
    total_expense = sum(t.amount for t in transactions if t.operation_type == 'EXPENSE')
    balance = total_income - total_expense
    
    # Группировка по категориям
    categories_summary = {}
    for transaction in transactions:
        category_name = transaction.category.name if transaction.category else 'Без категории'
        
        if category_name not in categories_summary:
            categories_summary[category_name] = {
                'income': 0.0,
                'expense': 0.0,
                'category_type': transaction.category.operation_type if transaction.category else 'EXPENSE'
            }
        
        if transaction.operation_type == 'INCOME':
            categories_summary[category_name]['income'] += transaction.amount
        else:
            categories_summary[category_name]['expense'] += transaction.amount
    
    return jsonify({
        'status': 'success',
        'data': {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'transaction_count': len(transactions),
            'categories_summary': categories_summary,
            'period': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
    })