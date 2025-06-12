# Redis & Celery Integration Guide

## 🚀 Обзор

Ваше приложение теперь включает:
- **Redis** для кеширования и брокера сообщений
- **Celery** для асинхронных фоновых задач
- **Flower** для мониторинга Celery

## 🛠️ Новые возможности

### 📊 Кеширование (Redis)
- Кеширование списка задач пользователя (5 минут)
- Кеширование отдельных задач (5 минут)
- Кеширование статистики (1 час)
- Автоматическая инвалидация кеша при изменениях

### 🔄 Фоновые задачи (Celery)
- **Напоминания о задачах** - автоматические уведомления за день до дедлайна
- **Статистика задач** - фоновая обработка статистики
- **Проверка просроченных задач** - каждый час
- **Ежедневная очистка** - удаление старых кешированных данных
- **Экспорт задач** - асинхронный экспорт в JSON
- **Массовое обновление** - обновление нескольких задач одновременно

## 🐳 Запуск с Docker

```bash
# Запуск всех сервисов
docker-compose up -d

# Только основные сервисы (без Flower)
docker-compose up -d app db redis celery-worker celery-beat
```

## 💻 Локальная разработка

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Запуск Redis (если не используете Docker)
```bash
redis-server
```

### 3. Запуск Celery Worker
```bash
celery -A src.celery_app worker --loglevel=info
```

### 4. Запуск Celery Beat (планировщик)
```bash
celery -A src.celery_app beat --loglevel=info
```

### 5. Запуск Flower (мониторинг)
```bash
celery -A src.celery_app flower --port=5555
```

### 6. Запуск FastAPI приложения
```bash
uvicorn src.main:app --reload
```

## 🌐 Доступные URL

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Flower (Celery Monitor)**: http://localhost:5555
- **Health Check**: http://localhost:8000/health
- **Cache Status**: http://localhost:8000/cache/status

## 📊 Новые API эндпоинты

### Статистика задач
```http
GET /tasks/statistics
```

### Экспорт задач
```http
POST /tasks/export?export_format=json
```

### Статус экспорта
```http
GET /tasks/export-status/{task_id}
```

### Массовое обновление
```http
POST /tasks/bulk-update
Content-Type: application/json

{
  "task_ids": [1, 2, 3],
  "update_data": {"completed": true}
}
```

## 🔧 Конфигурация

### Переменные окружения
```bash
# Redis
REDIS_URL=redis://localhost:6379/0

# Если используете Docker
REDIS_URL=redis://redis:6379/0
```

### Настройки кеширования
В `src/config.py`:
```python
cache_ttl: int = 300  # 5 минут по умолчанию
```

## 📋 Celery задачи

### Доступные задачи:
1. `send_task_reminder` - отправка напоминаний
2. `process_task_statistics` - обработка статистики
3. `check_overdue_tasks` - проверка просроченных задач
4. `daily_cleanup` - ежедневная очистка
5. `export_user_tasks` - экспорт задач пользователя
6. `bulk_update_tasks` - массовое обновление

### Расписание (Celery Beat):
- **Проверка просроченных задач**: каждый час
- **Ежедневная очистка**: каждый день в 2:00

## 🔍 Мониторинг

### Flower Dashboard
Откройте http://localhost:5555 для мониторинга:
- Активные воркеры
- Выполняющиеся задачи
- История задач
- Статистика производительности

### Health Check
```http
GET /health
```
Возвращает статус базы данных и Redis.

### Cache Status
```http
GET /cache/status  
```
Проверяет работу кеширования.

## 🚨 Примеры использования

### Создание задачи с напоминанием
```python
# Создайте задачи с дедлайном через API
# Автоматически будет запланировано напоминание за день до дедлайна
```

### Ручной запуск задач
```python
from src.tasks.celery_tasks import process_task_statistics

# Обновить статистику
process_task_statistics.delay()
```

### Кеширование в коде
```python
from src.redis_client import redis_client

# Сохранить в кеш
await redis_client.set("my_key", {"data": "value"}, ttl=300)

# Получить из кеша
data = await redis_client.get("my_key")
```

## 🔒 Безопасность

В продакшене обязательно:
1. Настройте аутентификацию для Redis
2. Используйте защищенные соединения
3. Ограничьте доступ к Flower
4. Настройте правильные CORS политики

## 🐛 Отладка

### Проверка соединения с Redis
```bash
redis-cli ping
```

### Логи Celery Worker
```bash
celery -A src.celery_app worker --loglevel=debug
```

### Просмотр очереди задач
```bash
redis-cli
> LLEN celery
> LRANGE celery 0 -1
```

## 📈 Производительность

- **Redis кеш** значительно ускоряет получение задач
- **Фоновые задачи** не блокируют API запросы
- **Статистика** обновляется асинхронно
- **Напоминания** обрабатываются автоматически

Теперь ваше приложение готово к высоким нагрузкам! 🎉 