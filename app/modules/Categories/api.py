from . import *
from flask_jwt_extended import get_jwt_identity, current_user


@api_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    print('sadasdasddas')
    """Получить все категории пользователя"""
    categories = Category.query.filter_by(user_id=current_user.id).all()
    
    # Используем ваш существующий метод to_dict()
    return jsonify({
        'status': 'success',
        'data': [category.to_dict() for category in categories]
    })

@api_bp.route('/categories/<int:category_id>', methods=['GET'])
@jwt_required()
def get_category(category_id):
    """Получить одну категорию"""
    category = Category.query.filter_by(
        id=category_id, 
        user_id=current_user.id
    ).first()
    
    if not category:
        return jsonify({'status': 'error', 'message': 'Категория не найдена'}), 404
    
    return jsonify({
        'status': 'success',
        'data': category.to_dict()
    })

@api_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    """Создать новую категорию"""
    data = request.get_json()
    
    # Простейшая валидация
    if not data or not data.get('name') or not data.get('operation_type'):
        return jsonify({'status': 'error', 'message': 'Необходимо указать name и operation_type'}), 400
    
    # Проверка типа операции
    if data['operation_type'] not in ['INCOME', 'EXPENSE']:
        return jsonify({'status': 'error', 'message': 'operation_type должен быть INCOME или EXPENSE'}), 400
    
    # Проверка уникальности (если нужно)
    existing = Category.query.filter_by(
        name=data['name'],
        operation_type=data['operation_type'],
        user_id=current_user.id
    ).first()
    
    if existing:
        return jsonify({'status': 'error', 'message': 'Такая категория уже существует'}), 400
    
    # Создаем новую категорию
    category = Category(
        name=data['name'],
        operation_type=data['operation_type'],
        user_id=current_user.id
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'data': category.to_dict()
    }), 201  # 201 = Created

@api_bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """Обновить категорию"""
    category = Category.query.filter_by(
        id=category_id,
        user_id=current_user.id
    ).first()
    
    if not category:
        return jsonify({'status': 'error', 'message': 'Категория не найдена'}), 404
    
    data = request.get_json()
    
    # Обновляем только переданные поля
    if 'name' in data:
        category.name = data['name']
    
    if 'operation_type' in data:
        if data['operation_type'] not in ['INCOME', 'EXPENSE']:
            return jsonify({'status': 'error', 'message': 'Некорректный тип операции'}), 400
        
        # Проверка, можно ли менять тип, если есть транзакции
        if category.transactions.count() > 0 and data['operation_type'] != category.operation_type:
            return jsonify({'status': 'error', 'message': 'Нельзя менять тип операции у категории с транзакциями'}), 400
        
        category.operation_type = data['operation_type']
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'data': category.to_dict()
    })

@api_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """Удалить категорию"""
    category = Category.query.filter_by(
        id=category_id,
        user_id=current_user.id
    ).first()
    
    if not category:
        return jsonify({'status': 'error', 'message': 'Категория не найдена'}), 404
    
    # Проверяем, есть ли связанные транзакции
    if category.transactions.count() > 0:
        return jsonify({
            'status': 'error', 
            'message': 'Нельзя удалить категорию с транзакциями'
        }), 400
    
    try:
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Категория успешно удалена'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Ошибка при удалении категории: {str(e)}'
        }), 500