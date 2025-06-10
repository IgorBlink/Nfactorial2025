# Railway Deployment - Простые шаги

## 1. Создай новый проект в Railway
1. Зайди на https://railway.app
2. Нажми "New Project"
3. Выбери "Deploy from GitHub repo"
4. Выбери свой репозиторий

## 2. Добавь PostgreSQL
1. В проекте нажми "Add Service"
2. Выбери "PostgreSQL"
3. Дождись создания

## 3. Настрой переменные окружения
В настройках веб-сервиса добавь:
- `SECRET_KEY` = `your-secret-key-here-123456789`
- `DATABASE_URL` = (скопируй из настроек PostgreSQL)

## 4. Задеплой
1. Нажми "Deploy"
2. Дождись завершения
3. Открой URL проекта

## 5. Инициализируй базу данных
Открой `https://твой-домен.railway.app/init-db` в браузере

Готово! 🚀 