# Документация API для FinanseManager

## Общая информация

API FinanseManager предоставляет RESTful интерфейс для управления финансовыми транзакциями и категориями. Все запросы и ответы используют формат JSON.

### Базовый URL

```
/api/
```

### Аутентификация

Большинство эндпоинтов требуют аутентификации с использованием JWT токенов. Токен передается в заголовке `Authorization`:

```
Authorization: Bearer <ваш_токен>
```

Для получения токена используйте эндпоинт `/auth/login`.

## Эндпоинты

### Аутентификация

#### POST /auth/login

Аутентификация пользователя и выдача JWT-токена.

**Тело запроса:**
```json
{
  "email_or_login": "string",
  "password": "string"
}
```

**Ответы:**
- 200: Успешная аутентификация
  ```json
  {
    "status": "success",
    "access_token": "string",
    "user": {
      "id": "integer",
      "login": "string",
      "email": "string"
    }
  }
  ```
- 400: Некорректные данные запроса
- 401: Неверные учетные данные

### Транзакции

#### GET /transactions

Получить все транзакции пользователя.

**Параметры запроса:**
- `category_id` (integer, опционально): Фильтр по ID категории
- `operation_type` (string, опционально): Фильтр по типу операции (INCOME или EXPENSE)
- `start_date` (string, опционально): Фильтр по начальной дате (ISO формат)
- `end_date` (string, опционально): Фильтр по конечной дате (ISO формат)
- `page` (integer, опционально, по умолчанию 1): Номер страницы
- `per_page` (integer, опционально, по умолчанию 20): Количество элементов на странице

**Ответы:**
- 200: Список транзакций
  ```json
  {
    "status": "success",
    "data": [
      {
        "id": "integer",
        "amount": "float",
        "description": "string",
        "operation_type": "string",
        "category_id": "integer",
        "user_id": "integer",
        "date": "string"
      }
    ],
    "pagination": {
      "page": "integer",
      "per_page": "integer",
      "total": "integer",
      "pages": "integer"
    }
  }
  ```

#### GET /transactions/{transaction_id}

Получить одну транзакцию по ID.

**Ответы:**
- 200: Данные транзакции
  ```json
  {
    "status": "success",
    "data": {
      "id": "integer",
      "amount": "float",
      "description": "string",
      "operation_type": "string",
      "category_id": "integer",
      "user_id": "integer",
      "date": "string"
    }
  }
  ```
- 404: Транзакция не найдена

#### POST /transactions

Создать новую транзакцию.

**Тело запроса:**
```json
{
  "amount": "float",
  "description": "string (опционально)",
  "operation_type": "string (INCOME или EXPENSE)",
  "category_id": "integer",
  "date": "string (опционально, ISO формат)"
}
```

**Ответы:**
- 201: Транзакция создана успешно
  ```json
  {
    "status": "success",
    "data": {
      "id": "integer",
      "amount": "float",
      "description": "string",
      "operation_type": "string",
      "category_id": "integer",
      "user_id": "integer",
      "date": "string"
    }
  }
  ```
- 400: Некорректные данные запроса
- 404: Категория не найдена

#### PUT /transactions/{transaction_id}

Обновить транзакцию.

**Тело запроса:**
```json
{
  "amount": "float (опционально)",
  "description": "string (опционально)",
  "operation_type": "string (опционально, INCOME или EXPENSE)",
  "category_id": "integer (опционально)",
  "date": "string (опционально, ISO формат)"
}
```

**Ответы:**
- 200: Транзакция обновлена успешно
  ```json
  {
    "status": "success",
    "data": {
      "id": "integer",
      "amount": "float",
      "description": "string",
      "operation_type": "string",
      "category_id": "integer",
      "user_id": "integer",
      "date": "string"
    }
  }
  ```
- 400: Некорректные данные запроса
- 404: Транзакция не найдена

#### DELETE /transactions/{transaction_id}

Удалить транзакцию.

**Ответы:**
- 200: Транзакция удалена успешно
  ```json
  {
    "status": "success",
    "message": "Транзакция удалена"
  }
  ```
- 404: Транзакция не найдена

#### GET /transactions/summary

Получить сводку по транзакциям (доходы/расходы за период).

**Параметры запроса:**
- `start_date` (string, опционально): Начальная дата (ISO формат)
- `end_date` (string, опционально): Конечная дата (ISO формат)

**Ответы:**
- 200: Сводка по транзакциям
  ```json
  {
    "status": "success",
    "data": {
      "total_income": "float",
      "total_expense": "float",
      "balance": "float",
      "transaction_count": "integer",
      "categories_summary": {
        "category_name": {
          "income": "float",
          "expense": "float",
          "category_type": "string"
        }
      },
      "period": {
        "start_date": "string",
        "end_date": "string"
      }
    }
  }
  ```

### Категории

#### GET /categories

Получить все категории пользователя.

**Ответы:**
- 200: Список категорий
  ```json
  {
    "status": "success",
    "data": [
      {
        "id": "integer",
        "name": "string",
        "operation_type": "string",
        "user_id": "integer"
      }
    ]
  }
  ```

#### GET /categories/{category_id}

Получить одну категорию по ID.

**Ответы:**
- 200: Данные категории
  ```json
  {
    "status": "success",
    "data": {
      "id": "integer",
      "name": "string",
      "operation_type": "string",
      "user_id": "integer"
    }
  }
  ```
- 404: Категория не найдена

#### POST /categories

Создать новую категорию.

**Тело запроса:**
```json
{
  "name": "string",
  "operation_type": "string (INCOME или EXPENSE)"
}
```

**Ответы:**
- 201: Категория создана успешно
  ```json
  {
    "status": "success",
    "data": {
      "id": "integer",
      "name": "string",
      "operation_type": "string",
      "user_id": "integer"
    }
  }
  ```
- 400: Некорректные данные запроса

#### PUT /categories/{category_id}

Обновить категорию.

**Тело запроса:**
```json
{
  "name": "string (опционально)",
  "operation_type": "string (опционально, INCOME или EXPENSE)"
}
```

**Ответы:**
- 200: Категория обновлена успешно
  ```json
  {
    "status": "success",
    "data": {
      "id": "integer",
      "name": "string",
      "operation_type": "string",
      "user_id": "integer"
    }
  }
  ```
- 400: Некорректные данные запроса
- 404: Категория не найдена