from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Личный кабинет")],
            [KeyboardButton(text="Подписки")],
            [KeyboardButton(text="Задать вопрос")]
        ],
        resize_keyboard=True
    )