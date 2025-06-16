from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import asyncio
import uvicorn

# Загружаем переменные окружения
load_dotenv()

app = FastAPI(title="Voice AI Agent", description="Голосовой AI агент с Gemini")

# Настройка статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Настройка Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY не найден в переменных окружения")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

class ChatMessage(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Главная страница приложения"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat_with_gemini(chat_message: ChatMessage):
    """Обработка текстового сообщения через Gemini"""
    try:
        response = model.generate_content(
            f"Ты дружелюбный AI ассистент. Отвечай на русском языке кратко и по делу. Пользователь сказал: {chat_message.message}"
        )
        
        return JSONResponse(content={
            "response": response.text,
            "status": "success"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обращении к Gemini: {str(e)}")

@app.get("/health")
async def health_check():
    """Проверка состояния сервера"""
    return {"status": "healthy", "message": "Сервер работает", "mode": "gemini"}

if __name__ == "__main__":
    # Получаем порт из переменной окружения (Railway) или используем 8001 по умолчанию
    port = int(os.getenv("PORT", 8001))
    
    print("🎤 Запуск полной версии Voice AI Agent с Gemini")
    print(f"🌐 Сервер запускается на порту {port}")
    print("🤖 Gemini AI подключен и готов к работе!")
    
    uvicorn.run(app, host="0.0.0.0", port=port) 