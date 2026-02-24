import requests
import json
from .utils import get_auth_headers

# Получаем базовый URL из конфигурации
from .config import BASE_URL

def get_tags():
    """Получить все теги пользователя"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/tags"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("Теги получены успешно:")
        for tag in data.get("data", []):
            print(f"  - {tag['name']} (ID: {tag['id']})")
        return data
    else:
        print(f"Ошибка получения тегов: {response.status_code} - {response.text}")
        return None

def create_tag(name):
    """Создать новый тег"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/tags"
    payload = {"name": name}
    headers.update({"Content-Type": "application/json"})
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        print(f"Тег '{name}' создан успешно: ID {data['data']['id']}")
        return data
    else:
        print(f"Ошибка создания тега: {response.status_code} - {response.text}")
        return None

def get_tag(tag_id):
    """Получить один тег по ID"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/tags/{tag_id}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        tag = data.get("data")
        print(f"Тег получен: {tag['name']} (ID: {tag['id']})")
        return data
    else:
        print(f"Ошибка получения тега: {response.status_code} - {response.text}")
        return None

def update_tag(tag_id, new_name):
    """Обновить название тега"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/tags/{tag_id}"
    payload = {"name": new_name}
    headers.update({"Content-Type": "application/json"})
    
    response = requests.put(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Тег {tag_id} обновлён на '{new_name}'")
        return data
    else:
        print(f"Ошибка обновления тега: {response.status_code} - {response.text}")
        return None

def delete_tag(tag_id):
    """Удалить тег"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/tags/{tag_id}"
    
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Тег {tag_id} удалён успешно")
        return data
    else:
        print(f"Ошибка удаления тега: {response.status_code} - {response.text}")
        return None

def run_tag_tests():
    """Запуск тестов для тегов"""
    print("\n--- Тесты тегов ---")
    
    # Получение списка тегов (должен быть пустым или содержать существующие)
    get_tags()
    
    # Создание двух тестовых тегов с уникальными именами
    import time
    timestamp = int(time.time())
    tag1 = create_tag(f"Работа_{timestamp}")
    tag2 = create_tag(f"Личное_{timestamp}")
    tag_ids = []
    if tag1 and tag2:
        tag_ids = [tag1['data']['id'], tag2['data']['id']]
        
        # Получение одного тега
        get_tag(tag_ids[0])
        
        # Обновление тега
        update_tag(tag_ids[0], f"Проект_{timestamp}")
        
        # Проверка обновления
        get_tag(tag_ids[0])
        
        # Удаление тегов
        for tid in tag_ids:
            delete_tag(tid)
        
        return True
    return False