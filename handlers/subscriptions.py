import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from db import get_user_token_by_user_id
from messages import GREET_MESSAGE, get_subscriptions_from_api
from keyboards import main_menu, get_payment_link_keyboard
from api.requests import FitnessAuthRequest, FitnessSubscriptionRequest

logger = logging.getLogger(__name__)

router = Router()

logger.info("🔧 subscriptions_router создан и обработчики зарегистрированы")


async def get_subscription_keyboard(user_token: str = ""):
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
            [InlineKeyboardButton(text="✅ Оформить подписку", callback_data=f"buy_subscription:{subscription_id}")],
            [InlineKeyboardButton(text="🔙 Назад к подпискам", callback_data="back_to_subscriptions")]
        ]
    )


# Более специфичные хэндлеры должны быть в начале
@router.message(F.text == "Подписки")
async def subscriptions_handler(message: Message, state: FSMContext):
    """Обработчик раздела подписок"""
    logger.info(f"🔍 subscriptions_handler вызван! user_id={message.from_user.id}, text='{message.text}'")
    await state.clear()
    
    # Получаем user_token из базы данных пользователя
    user_data = get_user_token_by_user_id(message.from_user.id)
    user_token = user_data.get('user_token') if user_data else None
    
    keyboard, subscriptions = await get_subscription_keyboard(user_token)
    await message.answer(GREET_MESSAGE, reply_markup=keyboard)


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


@router.message(lambda message: message.text not in ["Личный кабинет", "Подписки", "Задать вопрос", "🏠 В главное меню", "❌ Завершить диалог"])
async def subscription_variant_handler(message: Message, state: FSMContext):
    """Обработка выбора варианта подписки"""
    logger.info(f"🔍 subscription_variant_handler вызван! user_id={message.from_user.id}, text='{message.text}'")
    
    # Получаем актуальные данные подписок
    user_data = get_user_token_by_user_id(message.from_user.id)
    user_token = user_data.get('user_token') if user_data else None
    subscriptions = await get_subscriptions_from_api(user_token)
    
    # Находим выбранный тариф по названию
    selected_variant = None
    for variant in subscriptions:
        logger.debug(f"🔍 Проверяем вариант: {variant['title']}")
        logger.debug(f"🔍 Сравниваем с текстом сообщения: {message.text}")
        if variant['title'] == message.text:
            selected_variant = variant
            break
    
    if not selected_variant:
        return
    
    # Получаем детальную информацию о подписке
    try:
        fitness_request = FitnessSubscriptionRequest(user_token=user_token)
        details = await fitness_request.get_subscription_details(selected_variant['sub_id'])
        logger.debug(f"🔍 Получены детали подписки: {details}")
        
        if details and details.get("subscription"):
            sub_details = details["subscription"]
            logger.debug(f"🔍 Детали подписки: {sub_details}")
            
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
        logger.error(f"Ошибка получения деталей подписки: {e}")
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
async def buy_subscription_handler(callback: CallbackQuery):
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
        sub_id = selected_subscription['sub_id']
        sub_name = selected_subscription['title']
        sub_price = selected_subscription['price']
        sub_fee_id = selected_subscription.get('fee', {}).get('id', '')
        sub_fee_title = selected_subscription.get('fee', {}).get('title', '')
        sub_fee_price = selected_subscription.get('fee', {}).get('price', 0)
        total_price = int(sub_fee_price) + int(sub_price)

        pay_message = f"""
💳 <b>Оформление подписки</b>

Вы выбрали: <b>{sub_name}</b>

💰 К оплате:
• {sub_fee_title}: {sub_fee_price} ₽ (разово)
• Абонемент на месяц: {sub_price} ₽
———————————————————
ИТОГО: {total_price} ₽

⬇️ Нажмите на кнопку ниже, чтобы оплатить:
"""

        if not user_token:
            await callback.message.answer("❌ Ошибка при получении ссылки на оплату. Пожалуйста, попробуйте позже.", reply_markup=main_menu())
        else:
            fitness_request = FitnessSubscriptionRequest(user_token=user_token)
            url = await fitness_request.get_payment_link(
                subscription_id=sub_id,
                fee_id=sub_fee_id,
            )
            if not url:
                await callback.message.answer("❌ Ошибка при получении ссылки на оплату. Пожалуйста, попробуйте позже.", reply_markup=main_menu())
            else:
                await callback.message.edit_text(pay_message, reply_markup=get_payment_link_keyboard(url=url, subscription_id=sub_id))


@router.callback_query(F.data.regexp(r"^check_payment:(.+)$"))
async def check_payment_handler(callback: CallbackQuery):
    subscription_id = callback.data.split(":")[1]
    user_token = get_user_token_by_user_id(callback.from_user.id).get('user_token', '')

    if user_token and subscription_id:
        fitness_request = FitnessSubscriptionRequest(user_token=user_token)
        payment_status = await fitness_request.check_payment(subscription_id)

        if payment_status:
            await callback.message.edit_text("✅ Спасибо! Ваш платеж успешно подтвержден.", reply_markup=main_menu())
        else:
            await callback.message.edit_text("❌ Платеж не выполден, если возникли проблемы, свяжитесь с администратором", reply_markup=main_menu())

