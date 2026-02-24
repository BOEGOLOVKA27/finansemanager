import requests
import json
from .config import BASE_URL, LOGIN, PASSWORD, auth_token

def authenticate():
    """Аутентификация и получение JWT токена"""
    global auth_token
    
    url = f"{BASE_URL}/auth/login"
    
    # ВАЖНО: Используем email_or_login вместо email
    payload = {
        "email_or_login": LOGIN,  # LOGIN может содержать email или логин
        "password": PASSWORD
    }
    
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)  # используем json= вместо data=
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get("status") == "success":
            auth_token = data.get("access_token")
            
            # Получаем информацию о пользователе (опционально)
            user_data = data.get("user", {})
            
            print(f"✅ Успешная аутентификация")
            print(f"   Пользователь: {user_data.get('login', 'N/A')}")
            print(f"   Email: {user_data.get('email', 'N/A')}")
            print(f"   Токен: {auth_token[:20]}...")
            
            return True
        else:
            print(f"❌ Ошибка в ответе API: {data.get('message', 'Неизвестная ошибка')}")
            return False
    else:
        print(f"❌ Ошибка HTTP {response.status_code}")
        try:
            error_data = response.json()
            print(f"   Сообщение: {error_data.get('message', response.text)}")
        except:
            print(f"   Ответ: {response.text}")
        return False

def get_auth_headers():
    """Получить заголовки авторизации"""
    if not auth_token:
        print("Ошибка: Нет токена аутентификации")
        return None
    return {"Authorization": f"Bearer {auth_token}"}