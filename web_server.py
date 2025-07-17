import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import sqlite3

from config import CLOUDPAYMENTS_PUBLIC_ID, logger
from db import get_user_by_id, DATABASE_PATH
from messages import SUBSCRIPTION_VARIANTS, START_PRICE, MASSIVE_SUCCESS

web_logger = logging.getLogger(__name__)

app = FastAPI()

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="public"), name="static")

class SuccessPayment(BaseModel):
    userId: str

class WebhookData(BaseModel):
    SubscriptionId: Optional[str] = None
    AccountId: Optional[str] = None

@app.get("/api/ping")
async def ping():
    return {"message": "pong"}

@app.get("/api/user")
async def get_user(id: str):
    if not id:
        raise HTTPException(status_code=400, detail="Missing id")
    
    user = get_user_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    sub_type = user.get('sub_type', 1)
    subscription = next((s for s in SUBSCRIPTION_VARIANTS if s['id'] == sub_type), SUBSCRIPTION_VARIANTS[0])
    
    return {
        **user,
        "title": subscription['title'],
        "price": subscription['price'],
        "start_price": START_PRICE,
    }

@app.post("/api/success")
async def payment_success(data: SuccessPayment):
    """Обработка успешной оплаты"""
    # Получаем пользователя и его chat_id
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT chat_id, fio, phone FROM users WHERE id = ?", (data.userId,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    chat_id, fio, phone = row
    
    try:
        # Импортируем бота здесь, чтобы избежать циклического импорта
        from bot import bot
        
        # Отправляем сообщение об успешной оплате
        await bot.send_message(chat_id, MASSIVE_SUCCESS)
        web_logger.info(f"✅ Сообщение об успешной оплате отправлено пользователю {chat_id}")
        return {"success": True}
    except Exception as e:
        web_logger.error(f"❌ Ошибка отправки сообщения: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@app.post("/api/cloudpayments/webhook")
async def cloudpayments_webhook(request: Request):
    """Webhook для CloudPayments"""
    event = await request.json()
    web_logger.info(f'🔔 WEBHOOK получен: {event}')
    
    # CloudPayments требует ответ 200 с JSON {code: 0}
    return {"code": 0}

@app.get("/payment")
async def payment_page(token: str):
    """Страница оплаты"""
    if not token:
        raise HTTPException(status_code=400, detail="Missing token")
    
    # Проверяем, существует ли пользователь
    user = get_user_by_id(token)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Читаем HTML файл и подставляем публичный ключ CloudPayments
    try:
        with open("public/payment/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Добавляем скрипт с публичным ключом
        script_tag = f'<script>window.CLOUDPAYMENTS_PUBLIC_ID = "{CLOUDPAYMENTS_PUBLIC_ID}";</script>'
        html_content = html_content.replace("</head>", f"{script_tag}</head>")
        
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Payment page not found")

def run_server():
    """Запуск веб-сервера"""
    web_logger.info("🌐 Веб-сервер запускается на порту 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_server() 