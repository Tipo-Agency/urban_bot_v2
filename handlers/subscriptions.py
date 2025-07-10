from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from db import get_user_token_by_user_id
from messages import GREET_MESSAGE, get_subscriptions_from_api
from keyboards import main_menu
from api.requests import FitnessAuthRequest

router = Router()


async def get_subscription_keyboard(user_token: str = None):
    """Создает клавиатуру с вариантами подписок из API"""
    # Получаем реальные данные подписок
    subscriptions = await get_subscriptions_from_api(user_token)
    
    keyboard = []
    for variant in subscriptions:
        keyboard.append([KeyboardButton(text=variant['title'])])
    
    # Добавляем кнопку возврата в главное меню
    keyboard.append([KeyboardButton(text="🏠 В главное меню")])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    ), subscriptions


def get_buy_keyboard(subscription_id: str):
    """Создает инлайн клавиатуру для покупки подписки"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Купить подписку", callback_data=f"buy_subscription:{subscription_id}")],
            [InlineKeyboardButton(text="🔙 Назад к подпискам", callback_data="back_to_subscriptions")]
        ]
    )


@router.message(F.text == "🏠 В главное меню")
async def back_to_main_menu_handler(message: Message, state: FSMContext):
    """Обработчик возврата в главное меню"""
    await state.clear()
    
    greeting_text = f"""
🏠 <b>Главное меню</b>

Добро пожаловать, <b>{message.from_user.first_name}</b>!
Выберите, что вас интересует:
"""
    
    await message.answer(greeting_text, reply_markup=main_menu())


@router.callback_query(F.data == "back_to_main")
async def back_to_main_callback_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик возврата в главное меню через callback кнопку"""
    await callback.answer()
    await state.clear()
    
    greeting_text = f"""
🏠 <b>Главное меню</b>

Добро пожаловать, <b>{callback.from_user.first_name}</b>!
Выберите, что вас интересует:
"""
    
    await callback.message.answer(greeting_text, reply_markup=main_menu())
    await callback.message.delete()


@router.message(F.text == "Подписки")
async def subscriptions_handler(message: Message, state: FSMContext):
    """Обработчик раздела подписок"""
    await state.clear()
    
    # Получаем user_token из базы данных пользователя
    user_data = get_user_token_by_user_id(message.from_user.id)
    user_token = user_data.get('user_token') if user_data else None
    
    keyboard, subscriptions = await get_subscription_keyboard(user_token)
    await message.answer(GREET_MESSAGE, reply_markup=keyboard)


@router.callback_query(F.data == "back_to_subscriptions")
async def back_to_subscriptions_handler(callback: CallbackQuery, state: FSMContext):
    """Возврат к списку подписок"""
    await callback.answer()
    await state.clear()
    
    # Получаем user_token из базы данных пользователя
    user_data = get_user_token_by_user_id(callback.from_user.id)
    user_token = user_data.get('user_token') if user_data else None
    
    keyboard, subscriptions = await get_subscription_keyboard(user_token)
    await callback.message.answer(GREET_MESSAGE, reply_markup=keyboard)
    await callback.message.delete()


@router.message(F.text.regexp(r".*"))
async def subscription_variant_handler(message: Message, state: FSMContext):
    """Обработка выбора варианта подписки"""
    # Получаем актуальные данные подписок
    user_data = get_user_token_by_user_id(message.from_user.id)
    user_token = user_data.get('user_token') if user_data else None
    subscriptions = await get_subscriptions_from_api(user_token)
    
    # Находим выбранный тариф по названию
    selected_variant = None
    for variant in subscriptions:
        if variant['title'] == message.text.strip():
            selected_variant = variant
            break
    
    if not selected_variant:
        return
    
    # Получаем детальную информацию о подписке
    try:
        fitness_request = FitnessAuthRequest(user_token=user_token)
        details = await fitness_request.get_subscription_details(user_token or "", selected_variant['sub_id'])
        
        if details and details.get("subscription"):
            sub_details = details["subscription"]
            
            # Формируем подробное описание
            description = f"""
💳 <b>{sub_details.get('title', selected_variant['title'])}</b>

💰 <b>Стоимость:</b> {sub_details.get('price', selected_variant['price'])} ₽/мес

📋 <b>Описание:</b>
{sub_details.get('description', 'Описание недоступно')}

⏰ <b>Время доступа:</b>
{sub_details.get('available_time', 'Не указано')}

📅 <b>Период действия:</b>
{sub_details.get('validity_period', 'Не указано')}

⚠️ <b>Ограничения:</b>
{sub_details.get('restriction', 'Нет ограничений')}
"""
            
            # Добавляем информацию о вступительном взносе
            if sub_details.get('fee'):
                fee = sub_details['fee']
                description += f"\n💸 <b>Вступительный взнос:</b> {fee.get('price', '3000')} ₽"
            
            await message.answer(
                description, 
                reply_markup=get_buy_keyboard(selected_variant['sub_id'])
            )
        else:
            # Если детали не получены, показываем базовую информацию
            basic_info = f"""
💳 <b>{selected_variant['title']}</b>

💰 <b>Стоимость:</b> {selected_variant['price']} ₽/мес

📋 <b>Описание:</b>
{selected_variant['description']}

💸 <b>Вступительный взнос:</b> 3000 ₽
"""
            await message.answer(
                basic_info, 
                reply_markup=get_buy_keyboard(selected_variant['sub_id'])
            )
            
    except Exception as e:
        print(f"Ошибка получения деталей подписки: {e}")
        # Показываем базовую информацию при ошибке
        basic_info = f"""
💳 <b>{selected_variant['title']}</b>

💰 <b>Стоимость:</b> {selected_variant['price']} ₽/мес

📋 <b>Описание:</b>
{selected_variant['description']}

💸 <b>Вступительный взнос:</b> 3000 ₽
"""
        await message.answer(
            basic_info, 
            reply_markup=get_buy_keyboard(selected_variant['sub_id'])
        )


@router.callback_query(F.data.regexp(r"^buy_subscription:(.+)$"))
async def buy_subscription_handler(callback: CallbackQuery, state: FSMContext):
    """Обработка покупки подписки"""
    await callback.answer()
    
    subscription_id = callback.data.split(":")[1]
    
    # Получаем данные пользователя
    user_data = get_user_token_by_user_id(callback.from_user.id)
    
    # Создаем ссылку на оплату
    user_id = callback.from_user.id
    
    # Получаем информацию о подписке для отображения цены
    user_token = user_data.get('user_token') if user_data else None
    subscriptions = await get_subscriptions_from_api(user_token)
    selected_subscription = next((s for s in subscriptions if s['sub_id'] == subscription_id), None)
    
    if selected_subscription:
        pay_message = f"""
💳 <b>Оформление подписки</b>

Вы выбрали: <b>{selected_subscription['title']}</b>

💰 <b>К оплате:</b>
• Вступительный взнос: 3000 ₽ (разово)
• Абонемент на месяц: {selected_subscription['price']} ₽
—————————————
ИТОГО: {3000 + selected_subscription['price']} ₽

⬇️ Нажмите на кнопку ниже, чтобы оплатить:
"""
    else:
        pay_message = """
💳 <b>Оформление подписки</b>

💰 <b>К оплате:</b>
• Вступительный взнос: 3000 ₽ (разово)
• Абонемент на месяц: уточняется
—————————————
ИТОГО: уточняется

⬇️ Нажмите на кнопку ниже, чтобы оплатить:
"""
    
    await callback.message.answer(pay_message, reply_markup=get_buy_keyboard(user_id))


