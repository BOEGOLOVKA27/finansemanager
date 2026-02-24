import requests
import json
from .utils import get_auth_headers

# Получаем базовый URL из конфигурации
from .config import BASE_URL

def get_tasks(completed=None, tag_ids=None):
    """Получить задачи с опциональной фильтрацией по статусу и тегам"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/tasks"
    params = {}
    if completed is not None:
        params['completed'] = str(completed).lower()
    if tag_ids:
        params['tag_ids'] = ','.join(str(id) for id in tag_ids)
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print("Задачи получены успешно:")
        for task in data.get("data", []):
            tags = [t['name'] for t in task.get('tags', [])]
            print(f"  - {task['title']} (completed: {task['completed']}, tags: {tags})")
        return data
    else:
        print(f"Ошибка получения задач: {response.status_code} - {response.text}")
        return None

def create_task(title, description="", completed=False, tag_ids=None):
    """Создать новую задачу"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/tasks"
    payload = {
        "title": title,
        "description": description,
        "completed": completed
    }
    if tag_ids:
        payload["tag_ids"] = tag_ids
    
    headers.update({"Content-Type": "application/json"})
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        print(f"Задача '{title}' создана успешно: ID {data['data']['id']}")
        return data
    else:
        print(f"Ошибка создания задачи: {response.status_code} - {response.text}")
        return None

def get_task(task_id):
    """Получить одну задачу по ID"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/tasks/{task_id}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        task = data.get("data")
        tags = [t['name'] for t in task.get('tags', [])]
        print(f"Задача получена: {task['title']} (completed: {task['completed']}, tags: {tags})")
        return data
    else:
        print(f"Ошибка получения задачи: {response.status_code} - {response.text}")
        return None

def update_task(task_id, title=None, description=None, completed=None, tag_ids=None):
    """Обновить задачу"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/tasks/{task_id}"
    payload = {}
    if title is not None:
        payload["title"] = title
    if description is not None:
        payload["description"] = description
    if completed is not None:
        payload["completed"] = completed
    if tag_ids is not None:
        payload["tag_ids"] = tag_ids
    
    headers.update({"Content-Type": "application/json"})
    
    response = requests.put(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Задача {task_id} обновлена успешно")
        return data
    else:
        print(f"Ошибка обновления задачи: {response.status_code} - {response.text}")
        return None

def delete_task(task_id):
    """Удалить задачу"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/tasks/{task_id}"
    
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Задача {task_id} удалена успешно")
        return data
    else:
        print(f"Ошибка удаления задачи: {response.status_code} - {response.text}")
        return None

def get_tasks_summary():
    """Получить сводку по задачам"""
    headers = get_auth_headers()
    if not headers:
        return None
    
    url = f"{BASE_URL}/tasks/summary"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        summary = data.get("data")
        print("Сводка по задачам:")
        print(f"  Всего: {summary['total']}")
        print(f"  Выполнено: {summary['completed']}")
        print(f"  Ожидают: {summary['pending']}")
        return data
    else:
        print(f"Ошибка получения сводки: {response.status_code} - {response.text}")
        return None

def run_task_tests():
    """Запуск тестов для задач"""
    print("\n--- Тесты задач ---")
    
    # Получение задач (пусто)
    get_tasks()
    
    # Создание задачи без тегов
    task1 = create_task("Купить продукты", "Молоко, хлеб")
    
    # Создание тестовых тегов для задачи с тегами
    from .test_tags import create_tag
    import time
    timestamp = int(time.time())
    tag1 = create_tag(f"Работа_{timestamp}")
    tag2 = create_tag(f"Личное_{timestamp}")
    tag_ids = []
    task2 = None
    
    if tag1 and tag2:
        tag_ids = [tag1['data']['id'], tag2['data']['id']]
        
        # Создание задачи с тегами
        task2 = create_task(
            "Написать отчёт",
            "Сдать до пятницы",
            tag_ids=tag_ids
        )
    
    try:
        # Получение всех задач
        get_tasks()
        
        # Фильтрация по статусу
        get_tasks(completed=False)
        
        # Фильтрация по тегам (если есть теги)
        if tag_ids:
            get_tasks(tag_ids=[tag_ids[0]])
        
        # Получение одной задачи
        if task1:
            get_task(task1['data']['id'])
        
        # Обновление задачи
        if task1:
            update_task(task1['data']['id'], completed=True, description="Купить всё в магазине")
            get_task(task1['data']['id'])
        
        # Сводка по задачам
        get_tasks_summary()
        
        # Удаление задач
        if task1:
            delete_task(task1['data']['id'])
        if task2:
            delete_task(task2['data']['id'])
        
        return True
    finally:
        # Удаление тегов
        if tag_ids:
            from .test_tags import delete_tag
            for tid in tag_ids:
                delete_tag(tid)
    
    return False