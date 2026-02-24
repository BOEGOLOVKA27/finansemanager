#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Основной файл для запуска всех тестов API FinanseManager
"""

from .utils import authenticate
from .test_categories import run_category_tests
from .test_transactions import run_transaction_tests
from .test_tags import run_tag_tests
from .test_tasks import run_task_tests

def run_all_tests():
    """Запуск всех тестов API"""
    print("=== Запуск тестов API ===")
    
    # Аутентификация
    if not authenticate():
        return False
    
    # Запуск тестов по категориям
    print("\n--- Запуск тестов категорий ---")
    try:
        category_success = run_category_tests()
        if not category_success:
            print("❌ Тесты категорий не пройдены")
            return False
        print("✅ Тесты категорий пройдены успешно")
    except Exception as e:
        print(f"❌ Ошибка при выполнении тестов категорий: {e}")
        return False
    
    # Запуск тестов по транзакциям
    print("\n--- Запуск тестов транзакций ---")
    try:
        transaction_success = run_transaction_tests()
        if not transaction_success:
            print("❌ Тесты транзакций не пройдены")
            return False
        print("✅ Тесты транзакций пройдены успешно")
    except Exception as e:
        print(f"❌ Ошибка при выполнении тестов транзакций: {e}")
        return False
    
    # Запуск тестов по тегам
    print("\n--- Запуск тестов тегов ---")
    try:
        tag_success = run_tag_tests()
        if not tag_success:
            print("❌ Тесты тегов не пройдены")
            return False
        print("✅ Тесты тегов пройдены успешно")
    except Exception as e:
        print(f"❌ Ошибка при выполнении тестов тегов: {e}")
        return False
    
    # Запуск тестов по задачам
    print("\n--- Запуск тестов задач ---")
    try:
        task_success = run_task_tests()
        if not task_success:
            print("❌ Тесты задач не пройдены")
            return False
        print("✅ Тесты задач пройдены успешно")
    except Exception as e:
        print(f"❌ Ошибка при выполнении тестов задач: {e}")
        return False
    
    print("\n=== Все тесты завершены успешно ===")
    return True

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)