from flask import jsonify, request
from flask_jwt_extended import jwt_required, current_user
from datetime import datetime
from flask import jsonify, request
from flask_login import login_required
from . import *



# ==================== TAGS ====================

@api_bp.route('/tags', methods=['GET'])
@jwt_required()
def get_tags():
    """Получить все теги текущего пользователя"""
    tags = Tag.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'status': 'success',
        'data': [tag.to_dict() for tag in tags]
    })


@api_bp.route('/tags/<int:tag_id>', methods=['GET'])
@jwt_required()
def get_tag(tag_id):
    """Получить один тег"""
    tag = Tag.query.filter_by(id=tag_id, user_id=current_user.id).first()
    if not tag:
        return jsonify({'status': 'error', 'message': 'Тег не найден'}), 404
    return jsonify({'status': 'success', 'data': tag.to_dict()})


@api_bp.route('/tags', methods=['POST'])
@jwt_required()
def create_tag():
    """Создать новый тег"""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'status': 'error', 'message': 'Необходимо указать название тега'}), 400

    existing = Tag.query.filter_by(user_id=current_user.id, name=data['name']).first()
    if existing:
        return jsonify({'status': 'error', 'message': 'Тег с таким именем уже существует'}), 400

    tag = Tag(name=data['name'], user_id=current_user.id)
    try:
        db.session.add(tag)
        db.session.commit()
        return jsonify({'status': 'success', 'data': tag.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_bp.route('/tags/<int:tag_id>', methods=['PUT'])
@jwt_required()
def update_tag(tag_id):
    """Обновить тег"""
    tag = Tag.query.filter_by(id=tag_id, user_id=current_user.id).first()
    if not tag:
        return jsonify({'status': 'error', 'message': 'Тег не найден'}), 404

    data = request.get_json()
    if 'name' in data:
        existing = Tag.query.filter(
            Tag.id != tag_id,
            Tag.user_id == current_user.id,
            Tag.name == data['name']
        ).first()
        if existing:
            return jsonify({'status': 'error', 'message': 'Тег с таким именем уже существует'}), 400
        tag.name = data['name']

    try:
        db.session.commit()
        return jsonify({'status': 'success', 'data': tag.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_bp.route('/tags/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id):
    """Удалить тег"""
    tag = Tag.query.filter_by(id=tag_id, user_id=current_user.id).first()
    if not tag:
        return jsonify({'status': 'error', 'message': 'Тег не найден'}), 404

    try:
        db.session.delete(tag)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Тег удалён'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ==================== TASKS ====================

@api_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    """Получить задачи пользователя с фильтрацией и пагинацией"""
    query = Task.query.filter_by(user_id=current_user.id)

    # Фильтрация по статусу выполнения
    completed = request.args.get('completed')
    if completed is not None:
        if completed.lower() == 'true':
            query = query.filter_by(completed=True)
        elif completed.lower() == 'false':
            query = query.filter_by(completed=False)

    # Фильтрация по тегам (передать tag_ids через запятую)
    tag_ids = request.args.get('tag_ids')
    if tag_ids:
        try:
            ids = [int(id) for id in tag_ids.split(',')]
            query = query.filter(Task.tags.any(Tag.id.in_(ids)))
        except ValueError:
            pass

    # Сортировка: сначала новые (по дате создания)
    query = query.order_by(Task.created_at.desc())

    # Пагинация
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    tasks = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'status': 'success',
        'data': [task.to_dict() for task in tasks.items],
        'pagination': {
            'page': tasks.page,
            'per_page': tasks.per_page,
            'total': tasks.total,
            'pages': tasks.pages
        }
    })


@api_bp.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Получить одну задачу"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({'status': 'error', 'message': 'Задача не найдена'}), 404
    return jsonify({'status': 'success', 'data': task.to_dict()})


@api_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    """Создать новую задачу"""
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'status': 'error', 'message': 'Необходимо указать название задачи'}), 400

    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        completed=data.get('completed', False),
        user_id=current_user.id
    )

    # Привязка тегов (если передан список tag_ids)
    if 'tag_ids' in data and isinstance(data['tag_ids'], list):
        tags = Tag.query.filter(
            Tag.id.in_(data['tag_ids']),
            Tag.user_id == current_user.id
        ).all()
        if len(tags) != len(data['tag_ids']):
            return jsonify({'status': 'error', 'message': 'Один или несколько тегов не найдены или недоступны'}), 400
        task.tags = tags

    try:
        db.session.add(task)
        db.session.commit()
        return jsonify({'status': 'success', 'data': task.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_bp.route('/tasks/<int:task_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_task(task_id):
    """Обновить задачу"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({'status': 'error', 'message': 'Задача не найдена'}), 404

    data = request.get_json()

    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'completed' in data:
        task.completed = bool(data['completed'])

    # Обновление тегов
    if 'tag_ids' in data:
        if not isinstance(data['tag_ids'], list):
            return jsonify({'status': 'error', 'message': 'tag_ids должен быть списком'}), 400
        tags = Tag.query.filter(
            Tag.id.in_(data['tag_ids']),
            Tag.user_id == current_user.id
        ).all()
        if len(tags) != len(data['tag_ids']):
            return jsonify({'status': 'error', 'message': 'Один или несколько тегов не найдены или недоступны'}), 400
        task.tags = tags

    try:
        db.session.commit()
        return jsonify({'status': 'success', 'data': task.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Удалить задачу"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({'status': 'error', 'message': 'Задача не найдена'}), 404

    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Задача удалена'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_bp.route('/tasks/summary', methods=['GET'])
@jwt_required()
def get_tasks_summary():
    """Получить сводку по задачам"""
    total = Task.query.filter_by(user_id=current_user.id).count()
    completed = Task.query.filter_by(user_id=current_user.id, completed=True).count()
    pending = total - completed

    return jsonify({
        'status': 'success',
        'data': {
            'total': total,
            'completed': completed,
            'pending': pending
        }
    })


@api_bp.route('/tags/popular', methods=['GET'])
@jwt_required()
def get_popular_tags():
    """Получить самые используемые теги пользователя"""
    from sqlalchemy import func
    
    # Получаем теги, отсортированные по количеству использований в задачах
    popular_tags = db.session.query(
        Tag.id,
        Tag.name,
        func.count(task_tags.c.task_id).label('usage_count')
    ).outerjoin(
        task_tags,
        Tag.id == task_tags.c.tag_id
    ).filter(
        Tag.user_id == current_user.id
    ).group_by(
        Tag.id, Tag.name
    ).order_by(
        func.count(task_tags.c.task_id).desc(),
        Tag.created_at.desc()
    ).limit(5).all()
    
    return jsonify({
        'status': 'success',
        'data': [
            {'id': tag.id, 'name': tag.name, 'usage_count': tag.usage_count}
            for tag in popular_tags
        ]
    })