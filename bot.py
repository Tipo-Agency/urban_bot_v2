from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import support_router, auth_router, subscriptions_router, cabinet_router
from history import last_seen, chat_history, HISTORY_TIMEOUT
import time
import asyncio

# Создаем хранилище для FSM
storage = MemoryStorage()

dp = Dispatcher(storage=storage)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp.include_router(auth_router)
dp.include_router(cabinet_router)
dp.include_router(support_router)
dp.include_router(subscriptions_router)




async def auto_cleanup():
    while True:
        now = time.time()
        for uid in list(last_seen):
            if now - last_seen[uid] > HISTORY_TIMEOUT:
                print(f"[AUTO CLEANUP] Очистка истории для user_id={uid}")
                chat_history.pop(uid, None)
                last_seen.pop(uid, None)
        await asyncio.sleep(60)  # проверяем каждую минуту


async def on_startup(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать"),
        BotCommand(command="support", description="Спросить у поддержки")
    ])
    # Запускаем auto_cleanup в фоне
    asyncio.create_task(auto_cleanup())

if __name__ == "__main__":
    print("Bot started")
    dp.run_polling(bot, on_startup=on_startup)
