import logging
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Личный кабинет")],
            [KeyboardButton(text="Подписки")],
            # [KeyboardButton(text="Задать вопрос")]
        ],
        resize_keyboard=True
    )

def auth_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Регистрация", callback_data="register"),
                InlineKeyboardButton(text="Авторизация", callback_data="login")
            ]
        ]
    )

def get_cabinet_keyboard(ticket_id: str = "", is_subscriped: bool = False, is_freezed: bool = False):
    if not is_subscriped:
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Выбрать подписку", callback_data="select_subscription") 
            ],
            [
                InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main")
            ],
        ]
    if is_subscriped:
        inline_keyboard = [
            [
                # InlineKeyboardButton(text="Отменить подписку", callback_data=f"cancel_subscription:{ticket_id}"),
                InlineKeyboardButton(text="Заморозить подписку", callback_data=f"freeze_subscription:{ticket_id}") if not is_freezed else InlineKeyboardButton(text="Разморозить подписку", callback_data=f"unfreeze_subscription:{ticket_id}")
            ],
            [
                InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main")
            ]
        ]
    return InlineKeyboardMarkup(
        inline_keyboard=inline_keyboard
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

def confirm_freeze_subscription(ticket_id: str = ""):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да", callback_data=f"freeze_confirmed:{ticket_id}"),
                InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_subscriptions")
            ]
        ]
    )