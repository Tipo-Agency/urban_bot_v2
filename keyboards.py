import logging
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Личный кабинет")],
            [KeyboardButton(text="Подписки")],
            [KeyboardButton(text="Задать вопрос")]
        ],
        resize_keyboard=True
    )

def get_cabinet_keyboard(recurrent_id: str = ""):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Изменить подписку", callback_data="change_subscription"),
                InlineKeyboardButton(text="❌ Отменить подписку", callback_data=f"cancel_subscription:{recurrent_id}")
            ],
            [
                InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main")
            ],
        ]
    )

def get_payment_link_keyboard(url: str, subscription_id: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💳 Оплатить", url=url)
            ],
            [
                InlineKeyboardButton(text="✅ Я оплатил(а)", callback_data=f"check_payment:{subscription_id}"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_subscriptions")
            ],
        ]
    )

def confirm_cancel_subscription(recurrent_id: str = ""):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да", callback_data=f"cancel_confirmed:{recurrent_id}"),
                InlineKeyboardButton(text="🔙 Назад")
            ],
        ]
    )