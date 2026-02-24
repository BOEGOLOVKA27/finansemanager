import sys
import os

# Добавляем корневую директорию проекта в путь Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Базовый URL API
BASE_URL = "http://localhost:5000/api"

# Данные для аутентификации (можно изменить при необходимости)
LOGIN = "lome"
PASSWORD = "111111"

# Глобальная переменная для хранения токена
auth_token = None