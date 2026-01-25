from . import * 

from flask_jwt_extended import create_access_token
from datetime import timedelta
from flask import request, jsonify

@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    """Аутентификация пользователя и выдача JWT-токена"""
    data = request.get_json()
    
    # Получаем данные из запроса
    email_or_login = data.get('email_or_login')  # Можно принимать и email и login
    password = data.get('password')
    
    if not email_or_login or not password:
        return jsonify({'status': 'error', 'message': 'Необходимо указать email/логин и пароль'}), 400
    
    # Ищем пользователя по email ИЛИ login
    user = User.query.filter(
        (User.email == email_or_login) | (User.login == email_or_login)
    ).first()
    
    # Проверяем пользователя
    if user and user.check_password(password):
        # Создаем JWT токен с дополнительной информацией
        access_token = create_access_token(
            identity=f'{user.id}',
            expires_delta=timedelta(hours=24),
            additional_claims={
                'login': user.login,
                'email': user.email
            }
        )
        

        return jsonify({
            'status': 'success',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'login': user.login,
                'email': user.email
            }
        }), 200
    else:
        return jsonify({
            'status': 'error', 
            'message': 'Неверный email/логин или пароль'
        }), 401