#!/usr/bin/env python3
"""
Главный файл для запуска Telegram бота с веб-сервером для обработки платежей
"""

import asyncio
import threading
import signal
import sys

def run_web_server():
    """Запуск веб-сервера в отдельном потоке"""
    try:
        from web_server import run_server
        print("🌐 Starting web server...")
        run_server()
    except Exception as e:
        print(f"❌ Error starting web server: {e}")

def signal_handler(sig, frame):
    """Обработка сигнала завершения"""
    print('\n🛑 Shutting down...')
    sys.exit(0)

async def main():
    """Основная функция запуска"""
    # Обработка сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🤖 Starting Telegram Bot with Payment System...")
    print("📋 Features:")
    print("   - SQLite database for users")
    print("   - CloudPayments integration") 
    print("   - Web interface for payments")
    print("   - Subscription management")
    print()
    
    # Запускаем веб-сервер в отдельном потоке
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    # Даем веб-серверу время запуститься
    await asyncio.sleep(2)
    
    # Запускаем бота
    try:
        from bot import dp, bot, on_startup
        print("🚀 Bot is starting...")
        await on_startup(bot)
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}") 