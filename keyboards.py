from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Личный кабинет")],
            [KeyboardButton(text="Подписки")],
            [KeyboardButton(text="Задать вопрос")]
        ],
        resize_keyboard=True
    )

def get_cabinet_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Изменить подписку", callback_data="change_subscription"),
                InlineKeyboardButton(text="❌ Отменить подписку", callback_data="cancel_subscription")
            ],
            [
                InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main")
            ],
        ]
    )

def get_payment_link_keyboard(url: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💳 Оплатить", url=url)
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_subscriptions")
            ],
        ]
    )