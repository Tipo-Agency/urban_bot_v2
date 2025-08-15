import logging
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from messages import calculate_savings_percentage

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


def get_subscription_types_keyboard():
    """Создает клавиатуру с типами подписок"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💼 Дневная карта")],
            [KeyboardButton(text="🌟 Полный день")],
            [KeyboardButton(text="🏆 Все включено")],
            [KeyboardButton(text="🏠 В главное меню")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_subscription_periods_keyboard(subscription_type: str, subscriptions_list: list):
    """Создает клавиатуру с периодами подписок для выбранного типа"""
    keyboard = []
    
    for subscription in subscriptions_list:
        # Форматируем кнопку с указанием экономии если есть
        button_text = f"{subscription['period']} мес. — {subscription['price']} ₽"
        
        # Добавляем значок экономии для 6 и 12 месяцев
        if subscription['period'] == 6:
            saving_percent = calculate_savings_percentage(subscription['price'], subscription['price'] * 6, subscription['period'])
            button_text += f" (Экономия {saving_percent}%)"
        elif subscription['period'] == 12:
            saving_percent = calculate_savings_percentage(subscription['price'], subscription['price'] * 12, subscription['period'])
            button_text += f" (Экономия {saving_percent}%)"
            
        keyboard.append([KeyboardButton(text=button_text)])
    
    # Добавляем кнопки навигации
    keyboard.append([KeyboardButton(text="🔙 Назад к типам подписок")])
    keyboard.append([KeyboardButton(text="🏠 В главное меню")])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_subscription_buy_keyboard(subscription_id: str):
    """Создает инлайн клавиатуру для покупки конкретной подписки"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Оформить подписку", callback_data=f"buy_subscription:{subscription_id}")],
            [InlineKeyboardButton(text="🔙 Назад к периодам", callback_data="back_to_periods")],
            [InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main")]
        ]
    )