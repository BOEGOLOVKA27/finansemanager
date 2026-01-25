import requests
import json

# Базовый URL API
BASE_URL = "http://localhost:5000/api"

# Данные для аутентификации
LOGIN = "lome"
PASSWORD = "111111"

# Глобальная переменная для хранения токена
auth_token = None


def authenticate():
    """Аутентификация и получение JWT токена"""
    global auth_token
    
    url = f"{BASE_URL}/auth/login"
    
    # 👇 ВАЖНО: Используем email_or_login вместо email
    payload = {
        "email_or_login": LOGIN,  # LOGIN может содержать email или логин
        "password": PASSWORD
    }
    
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)  # 👈 используем json= вместо data=
    
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


def get_categories():
    """Получить все категории пользователя"""
    if not auth_token:
        print("Ошибка: Нет токена аутентификации")
        return None
    
    url = f"{BASE_URL}/categories"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
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
    if not auth_token:
        print("Ошибка: Нет токена аутентификации")
        return None
    
    url = f"{BASE_URL}/categories"
    payload = {
        "name": name,
        "operation_type": operation_type
    }
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
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
    if not auth_token:
        print("Ошибка: Нет токена аутентификации")
        return None
    
    url = f"{BASE_URL}/categories/{category_id}"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
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
    if not auth_token:
        print("Ошибка: Нет токена аутентификации")
        return None
    
    url = f"{BASE_URL}/categories/{category_id}"
    payload = {}
    if name:
        payload["name"] = name
    if operation_type:
        payload["operation_type"] = operation_type
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
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
    if not auth_token:
        print("Ошибка: Нет токена аутентификации")
        return None
    
    url = f"{BASE_URL}/categories/{category_id}"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"Категория {category_id} удалена успешно")
        return data
    else:
        print(f"Ошибка удаления категории: {response.status_code} - {response.text}")
        return None


def get_transactions():
    """Получить все транзакции пользователя"""
    if not auth_token:
        print("Ошибка: Нет токена аутентификации")
        return None
    
    url = f"{BASE_URL}/transactions"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("Транзакции получены успешно:")
        for transaction in data.get("data", []):
            print(f"  - {transaction['amount']} ({transaction['operation_type']}) - {transaction.get('description', '')}")
        return data
    else:
        print(f"Ошибка получения транзакций: {response.status_code} - {response.text}")
        return None


def create_transaction(amount, operation_type, category_id, description=""):
    """Создать новую транзакцию"""
    if not auth_token:
        print("Ошибка: Нет токена аутентификации")
        return None
    
    url = f"{BASE_URL}/transactions"
    payload = {
        "amount": amount,
        "operation_type": operation_type,
        "category_id": category_id,
        "description": description
    }
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        print(f"Транзакция создана успешно: {amount} ({operation_type})")
        return data
    else:
        print(f"Ошибка создания транзакции: {response.status_code} - {response.text}")
        return None


def get_transaction(transaction_id):
    """Получить одну транзакцию по ID"""
    if not auth_token:
        print("Ошибка: Нет токена аутентификации")
        return None
    
    url = f"{BASE_URL}/transactions/{transaction_id}"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        transaction = data.get("data")
        print(f"Транзакция получена: {transaction['amount']} ({transaction['operation_type']})")
        return data
    else:
        print(f"Ошибка получения транзакции: {response.status_code} - {response.text}")
        return None


def update_transaction(transaction_id, amount=None, description=None, operation_type=None, category_id=None):
    """Обновить транзакцию"""
    if not auth_token:
        print("Ошибка: Нет токена аутентификации")
        return None
    
    url = f"{BASE_URL}/transactions/{transaction_id}"
    payload = {}
    if amount is not None:
        payload["amount"] = amount
    if description is not None:
        payload["description"] = description
    if operation_type:
        payload["operation_type"] = operation_type
    if category_id:
        payload["category_id"] = category_id
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.put(url, data=json.dumps(payload), headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Транзакция {transaction_id} обновлена успешно")
        return data
    else:
        print(f"Ошибка обновления транзакции: {response.status_code} - {response.text}")
        return None


def delete_transaction(transaction_id):
    """Удалить транзакцию"""
    if not auth_token:
        print("Ошибка: Нет токена аутентификации")
        return None
    
    url = f"{BASE_URL}/transactions/{transaction_id}"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Транзакция {transaction_id} удалена успешно")
        return data
    else:
        print(f"Ошибка удаления транзакции: {response.status_code} - {response.text}")
        return None



def get_transactions_summary():
    """Получить сводку по транзакциям"""
    if not auth_token:
        print("Ошибка: Нет токена аутентификации")
        return None
    
    url = f"{BASE_URL}/transactions/summary"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        summary = data.get("data")
        print("Сводка по транзакциям:")
        print(f"  Доходы: {summary['total_income']}")
        print(f"  Расходы: {summary['total_expense']}")
        print(f"  Баланс: {summary['balance']}")
        print(f"  Количество транзакций: {summary['transaction_count']}")
        return data
    else:
        print(f"Ошибка получения сводки: {response.status_code} - {response.text}")
        return None


def run_all_tests():
    """Запуск всех тестов API"""
    print("=== Запуск тестов API ===")
    
    # Аутентификация
    if not authenticate():
        return
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
    
    print("\n--- Тесты транзакций ---")
    # Получение транзакций
    transactions_data = get_transactions()
    
    # Создание новой транзакции (если есть категории)
    if category_id:
        new_transaction = create_transaction(100.50, "EXPENSE", category_id, "Тестовая транзакция")
        transaction_id = None
        if new_transaction:
            transaction_id = new_transaction["data"]["id"]
            
            # Получение созданной транзакции
            get_transaction(transaction_id)
            
            # Обновление транзакции
            update_transaction(transaction_id, amount=150.75, description="Обновленная транзакция")
            
            # Получение обновленной транзакции
            get_transaction(transaction_id)
    
    print("\n--- Тесты сводки ---")
    # Получение сводки по транзакциям
    get_transactions_summary()
    
    # Удаление тестовой транзакции
    if 'transaction_id' in locals() and transaction_id:
        delete_transaction(transaction_id)
    
    # Удаление тестовой категории
    if category_id:
        delete_category(category_id)
    
    print("\n=== Тесты завершены ===")


if __name__ == "__main__":
    run_all_tests()