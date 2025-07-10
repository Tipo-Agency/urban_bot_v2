from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from services.gpt import get_llm_response
from history import chat_history, update_user_history
from keyboards import main_menu

router = Router()

active_gpt_users = set()

def get_support_keyboard():
    """Создает клавиатуру для режима поддержки"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Завершить диалог")],
            [KeyboardButton(text="🏠 В главное меню")]
        ],
        resize_keyboard=True
    )


@router.message(F.text == "Задать вопрос")
async def ask_handler(message: Message):
    user_id = message.from_user.id
    active_gpt_users.add(user_id)
    
    await message.answer(
        "💬 <b>Техническая поддержка</b>\n\nНапишите свой вопрос, и я постараюсь помочь!\n\n" + 
        "Для завершения диалога или возврата в меню используйте кнопки ниже.",
        reply_markup=get_support_keyboard()
    )


@router.message(F.text == "❌ Завершить диалог")
async def end_support_handler(message: Message):
    """Завершение диалога с поддержкой"""
    user_id = message.from_user.id
    active_gpt_users.discard(user_id)
    
    await message.answer(
        "✅ Диалог с поддержкой завершен.\n\nЕсли у вас еще есть вопросы, вы всегда можете обратиться снова!",
        reply_markup=main_menu()
    )


@router.message(F.text)
async def support_logic(message: Message):
    user_id = message.from_user.id

    # ⛔ не обрабатываем, если юзер не в режиме GPT
    if user_id not in active_gpt_users:
        return
    
    # ⛔ если пользователь нажал "🏠 В главное меню" - выходим из режима поддержки
    if message.text == "🏠 В главное меню":
        active_gpt_users.discard(user_id)
        return  # Обработка перейдет к handlers/subscriptions.py

    name = message.from_user.first_name or ""
    history = chat_history[user_id]

    await message.bot.send_chat_action(message.chat.id, action="typing")

    reply = await get_llm_response(message.text, telegram_name=name, history=history)
    
    await message.answer(reply, reply_markup=get_support_keyboard())

    update_user_history(user_id, message.text, reply)

    # ❌ после ответа — НЕ убираем из режима GPT, пользователь сам должен завершить диалог

