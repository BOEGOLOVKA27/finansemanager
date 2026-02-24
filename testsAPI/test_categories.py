import requests
import json
from .utils import get_auth_headers

# Получаем базовый URL из конфигурации
from .config import BASE_URL

def get_categories():
    """Получить все категории пользователя"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/categories"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("Категории получены успешно:")
        for category in data.get("data", []):
            print(f"  - {category['name']} ({category['operation_type']})")
        return data
    else:
        print(f"Ошибка получения категорий: {response.status_code} - {response.text}")
        return None

def create_category(name, operation_type):
    """Создать новую категорию"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/categories"
    payload = {
        "name": name,
        "operation_type": operation_type
    }
    headers.update({"Content-Type": "application/json"})
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        print(f"Категория '{name}' создана успешно: ID {data['data']['id']}")
        return data
    else:
        print(f"Ошибка создания категории: {response.status_code} - {response.text}")
        return None

def get_category(category_id):
    """Получить одну категорию по ID"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/categories/{category_id}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        category = data.get("data")
        print(f"Категория получена: {category['name']} ({category['operation_type']})")
        return data
    else:
        print(f"Ошибка получения категории: {response.status_code} - {response.text}")
        return None

def update_category(category_id, name=None, operation_type=None):
    """Обновить категорию"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/categories/{category_id}"
    payload = {}
    if name:
        payload["name"] = name
    if operation_type:
        payload["operation_type"] = operation_type
    
    headers.update({"Content-Type": "application/json"})
    
    response = requests.put(url, data=json.dumps(payload), headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Категория {category_id} обновлена успешно")
        return data
    else:
        print(f"Ошибка обновления категории: {response.status_code} - {response.text}")
        return None

def delete_category(category_id):
    """Удалить категорию"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/categories/{category_id}"
    
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"Категория {category_id} удалена успешно")
        return data
    else:
        print(f"Ошибка удаления категории: {response.status_code} - {response.text}")
        return None

def run_category_tests():
    """Запуск тестов для категорий"""
    print("\n--- Тесты категорий ---")
    
    # Получение категорий
    categories_data = get_categories()
    
    # Создание новой категории
    new_category = create_category("Тестовая категория", "EXPENSE")
    category_id = None
    if new_category:
        category_id = new_category["data"]["id"]
        
        # Получение созданной категории
        get_category(category_id)
        
        # Обновление категории
        update_category(category_id, name="Обновленная категория")
        
        # Получение обновленной категории
        get_category(category_id)
        
        # Удаление тестовой категории
        delete_category(category_id)
        
        return True
    return False