import requests
import json
from .utils import get_auth_headers

# Получаем базовый URL из конфигурации
from .config import BASE_URL

def get_transactions():
    """Получить все транзакции пользователя"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/transactions"
    
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
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/transactions"
    payload = {
        "amount": amount,
        "operation_type": operation_type,
        "category_id": category_id,
        "description": description
    }
    headers.update({"Content-Type": "application/json"})
    
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
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/transactions/{transaction_id}"
    
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
    headers = get_auth_headers()
    if not headers:
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
    
    headers.update({"Content-Type": "application/json"})
    
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
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/transactions/{transaction_id}"
    
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
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/transactions/summary"
    
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

def run_transaction_tests():
    """Запуск тестов для транзакций"""
    print("\n--- Тесты транзакций ---")
    
    # Создание тестовой категории для транзакций
    from .test_categories import create_category
    category = create_category("Тестовая категория для транзакций", "EXPENSE")
    if not category:
        print("Не удалось создать тестовую категорию")
        return False
    
    category_id = category["data"]["id"]
    
    try:
        # Получение транзакций
        transactions_data = get_transactions()
        
        # Создание новой транзакции
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
            
            # Удаление тестовой транзакции
            delete_transaction(transaction_id)
            
            return True
    finally:
        # Удаление тестовой категории
        from .test_categories import delete_category
        delete_category(category_id)
    
    return False