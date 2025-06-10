# Railway Database Fix

## Проблема: Connection refused [Errno 111]

Приложение не может подключиться к PostgreSQL базе данных.

## ✅ Решение:

### 1. Проверь статус через новые endpoints:

После деплоя открой:
- `https://your-app.railway.app/health` - должно быть `{"status": "healthy"}`  
- `https://your-app.railway.app/db-status` - покажет проблему
- `https://your-app.railway.app/auth/status` - статус auth системы

### 2. Возможные проблемы в `/db-status`:

**"DATABASE_URL not set":**
- В Railway Dashboard добавь PostgreSQL service
- Database → PostgreSQL → Deploy

**"Database connection failed":**
- PostgreSQL сервис еще разворачивается (подожди 2-3 минуты)
- Неправильный DATABASE_URL (Railway должен установить автоматически)

### 3. После исправления базы:

Вызови `POST https://your-app.railway.app/init-db` для создания таблиц.

## 🔍 Отладка:

1. **Railway Dashboard → Variables** - проверь что есть:
   - `DATABASE_URL` (создается автоматически при добавлении PostgreSQL)
   - `SECRET_KEY` (добавь вручную)

2. **Railway Dashboard → PostgreSQL service** - статус должен быть "Active"

3. **Logs** - должно быть: `🚀 Application starting...`

## ✅ Правильные статусы:

```json
// /db-status
{
  "database_url_set": true,
  "secret_key_set": true, 
  "connection_status": "connected",
  "message": "Database connection successful"
}

// /auth/status
{
  "auth_ready": true,
  "database_url_set": true,
  "secret_key_set": true,
  "message": "Auth system operational"
}
```

После этого фронтенд будет работать! 🎉 