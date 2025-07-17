#!/usr/bin/env python3
"""
Главный файл для запуска Telegram бота с веб-сервером для обработки платежей
"""

import asyncio
import threading
import signal
import sys
import logging
from config import logger

def run_web_server():
    """Запуск веб-сервера в отдельном потоке"""
    try:
        from web_server import run_server
        logger.info("🌐 Starting web server...")
        run_server()
    except Exception as e:
        logger.error(f"❌ Error starting web server: {e}")

def signal_handler(sig, frame):
    """Обработка сигнала завершения"""
    logger.info('🛑 Shutting down...')
    sys.exit(0)

async def main():
    """Основная функция запуска"""
    # Обработка сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🤖 Starting Telegram Bot with Payment System...")
    logger.info("📋 Features:")
    logger.info("   - SQLite database for users")
    logger.info("   - CloudPayments integration") 
    logger.info("   - Web interface for payments")
    logger.info("   - Subscription management")
    
    # Запускаем веб-сервер в отдельном потоке
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    # Даем веб-серверу время запуститься
    await asyncio.sleep(2)
    
    # Запускаем бота
    try:
        from bot import dp, bot, on_startup
        logger.info("🚀 Bot is starting...")
        await on_startup(bot)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Error starting bot: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}") 