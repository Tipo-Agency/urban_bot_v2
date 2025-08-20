import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from db import get_user_token_by_user_id
from messages import GREET_MESSAGE, get_subscriptions_from_api, group_subscriptions_by_type, format_subscription_with_savings
from keyboards import main_menu, get_payment_link_keyboard, get_subscription_types_keyboard, get_subscription_periods_keyboard, get_subscription_buy_keyboard
from api.requests import FitnessAuthRequest, FitnessSubscriptionRequest

logger = logging.getLogger(__name__)

router = Router()

logger.info("🔧 subscriptions_router создан и обработчики зарегистрированы")


# Глобальные переменные для хранения состояния
user_subscriptions_data = {}
user_selected_type = {}

async def get_grouped_subscriptions(user_token: str = ""):
    """Получает и группирует подписки из API"""
    subscriptions = await get_subscriptions_from_api(user_token)
    return group_subscriptions_by_type(subscriptions)


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
    
    # Получаем и сохраняем сгруппированные подписки
    grouped_subscriptions = await get_grouped_subscriptions(user_token)
    user_subscriptions_data[message.from_user.id] = grouped_subscriptions
    
    keyboard = get_subscription_types_keyboard()
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
    
    # Получаем и сохраняем сгруппированные подписки
    grouped_subscriptions = await get_grouped_subscriptions(user_token)
    user_subscriptions_data[callback.from_user.id] = grouped_subscriptions
    
    keyboard = get_subscription_types_keyboard()
    await callback.message.answer(GREET_MESSAGE, reply_markup=keyboard)
    await callback.message.delete()


# Обработчики для новой логики подписок
@router.message(F.text.in_(["🧪 Тестовая подписка", "💼 Дневная карта", "🌟 Полный день", "🏆 Все включено"]))
async def subscription_type_handler(message: Message, state: FSMContext):
    """Обработчик выбора типа подписки"""
    logger.info(f"🔍 subscription_type_handler вызван! user_id={message.from_user.id}, text='{message.text}'")
    
    # Определяем выбранный тип
    type_mapping = {
        "🧪 Тестовая подписка": "Тест",
        "💼 Дневная карта": "Дневная карта",
        "🌟 Полный день": "Полный день", 
        "🏆 Все включено": "Все включено"
    }
    
    selected_type = type_mapping.get(message.text)
    if not selected_type:
        return
        
    user_selected_type[message.from_user.id] = selected_type
    
    # Получаем подписки для выбранного типа
    grouped_subscriptions = user_subscriptions_data.get(message.from_user.id, {})
    subscriptions_for_type = grouped_subscriptions.get(selected_type, [])
    
    if not subscriptions_for_type:
        await message.answer(f"К сожалению, подписки типа '{selected_type}' сейчас недоступны.", reply_markup=get_subscription_types_keyboard())
        return
    
    # Для тестовой подписки показываем сразу детали
    if selected_type == "Тест":
        subscription = subscriptions_for_type[0]  # Тестовая подписка одна
        await show_test_subscription_details(message, subscription)
        return
    
    # Форматируем подписки с расчетом экономии
    monthly_subscription = next((s for s in subscriptions_for_type if s.get('period', 1) == 1), None)
    formatted_subscriptions = []
    
    for subscription in subscriptions_for_type:
        formatted_sub = format_subscription_with_savings(subscription, monthly_subscription)
        formatted_subscriptions.append(formatted_sub)
    
    # Создаем клавиатуру с периодами
    keyboard = get_subscription_periods_keyboard(selected_type, formatted_subscriptions)
    
    # Формируем сообщение с описанием типа подписки
    type_descriptions = {
        "Дневная карта": "💼 <b>Дневная карта</b>\n\nПосещение с 7:00 до 17:00, тренажёрный зал и кардио-зона.",
        "Полный день": "🌟 <b>Полный день</b>\n\nБезлимитное посещение в любое время, тренажёрный зал и кардио-зона.",
        "Все включено": "🏆 <b>Все включено</b>\n\nБезлимитное посещение, все групповые программы, спа-зона и скалодром."
    }
    
    description = type_descriptions.get(selected_type, f"<b>{selected_type}</b>")
    description += "\n\n💰 Выберите период подписки:"
    
    await message.answer(description, reply_markup=keyboard)


async def show_test_subscription_details(message: Message, subscription: dict):
    """Показывает детали тестовой подписки"""
    title = subscription.get('title', 'Тестовая подписка')
    price = subscription.get('price', 0)
    description = subscription.get('description', '')
    available_time = subscription.get('available_time', '')
    validity = subscription.get('validity', {})
    services = subscription.get('services', [])
    
    # Формируем описание
    details = f"""
🧪 <b>{title}</b>

💰 <b>Стоимость:</b> {price} ₽
⏰ <b>Срок действия:</b> {validity.get('validity_description', '1 день')}

📋 <b>Описание:</b>
{description if description else 'Тестовая подписка для знакомства с клубом'}

⏰ <b>Время доступа:</b>
{available_time if available_time else 'Не указано'}
"""
    
    # Добавляем информацию об услугах
    if services:
        details += "\n🎁 <b>Включенные услуги:</b>\n"
        for service in services:
            details += f"• {service.get('title', '')} - {service.get('count', 1)} шт.\n"
    
    # Добавляем информацию о вступительном взносе
    fee = subscription.get('fee', {})
    if fee and fee.get('price'):
        details += f"\n💸 <b>Вступительный взнос:</b> {fee.get('price')} ₽"
    
    # Создаем клавиатуру для покупки
    keyboard = get_subscription_buy_keyboard(subscription['sub_id'])
    
    await message.answer(details.strip(), reply_markup=keyboard)


@router.message(F.text == "🔙 Назад к типам подписок")
async def back_to_types_handler(message: Message, state: FSMContext):
    """Возврат к выбору типов подписок"""
    keyboard = get_subscription_types_keyboard()
    await message.answer(GREET_MESSAGE, reply_markup=keyboard)


@router.message(lambda message: message.text and ("мес. —" in message.text))
async def subscription_period_handler(message: Message, state: FSMContext):
    """Обработчик выбора периода подписки"""
    logger.info(f"🔍 subscription_period_handler вызван! user_id={message.from_user.id}, text='{message.text}'")
    
    # Извлекаем период и цену из текста кнопки
    try:
        # Формат: "1 мес. — 2400 ₽" или "6 мес. — 13900 ₽ 💰"
        parts = message.text.split(" мес. — ")
        if len(parts) != 2:
            return
            
        period = int(parts[0])
        price_part = parts[1].split(" ")[0]  # Убираем эмодзи
        price = int(price_part)
        
        # Находим соответствующую подписку
        selected_type = user_selected_type.get(message.from_user.id)
        if not selected_type:
            return
            
        grouped_subscriptions = user_subscriptions_data.get(message.from_user.id, {})
        subscriptions_for_type = grouped_subscriptions.get(selected_type, [])
        
        selected_subscription = None
        for subscription in subscriptions_for_type:
            if subscription.get('period') == period and subscription.get('price') == price:
                selected_subscription = subscription
                break
                
        if not selected_subscription:
            return
            
        # Формируем детальное описание подписки
        monthly_subscription = next((s for s in subscriptions_for_type if s.get('period', 1) == 1), None)
        formatted_sub = format_subscription_with_savings(selected_subscription, monthly_subscription)
        
        # Рассчитываем экономию если есть
        savings_info = ""
        if period > 1 and monthly_subscription:
            monthly_price = monthly_subscription.get('price', 0)
            if monthly_price > 0:
                total_monthly_cost = monthly_price * period
                savings = total_monthly_cost - price
                if savings > 0:
                    savings_percent = round((savings / total_monthly_cost) * 100)
                    savings_info = f"\n\n💰 <b>Ваша экономия:</b> {savings} ₽ ({savings_percent}%)"
        
        # Получаем детальную информацию о подписке
        user_data = get_user_token_by_user_id(message.from_user.id)
        user_token = user_data.get('user_token') if user_data else None
        
        description = f"""
💳 <b>{formatted_sub['title']}</b>

💰 <b>Стоимость:</b> {price} ₽
📅 <b>Период:</b> {period} мес.

📋 <b>Описание:</b>
{selected_subscription.get('description', 'Описание недоступно')}

⏰ <b>Время доступа:</b>
{selected_subscription.get('available_time', 'Не указано')}
{savings_info}
        """
        
        # Добавляем информацию о вступительном взносе
        fee = selected_subscription.get('fee', {})
        if fee and fee.get('price'):
            description += f"\n\n💸 <b>Вступительный взнос:</b> {fee.get('price')} ₽"
        
        await message.answer(
            description.strip(),
            reply_markup=get_subscription_buy_keyboard(selected_subscription['sub_id'])
        )
        
    except (ValueError, IndexError) as e:
        logger.error(f"Ошибка парсинга периода подписки: {e}")
        return


@router.callback_query(F.data == "back_to_periods")
async def back_to_periods_handler(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору периодов подписки"""
    await callback.answer()
    
    selected_type = user_selected_type.get(callback.from_user.id)
    if not selected_type:
        # Если тип не выбран, возвращаемся к типам
        keyboard = get_subscription_types_keyboard()
        await callback.message.edit_text(GREET_MESSAGE, reply_markup=None)
        await callback.message.answer(GREET_MESSAGE, reply_markup=keyboard)
        return
    
    # Для тестовой подписки возвращаемся к типам
    if selected_type == "Тест":
        keyboard = get_subscription_types_keyboard()
        await callback.message.edit_text(GREET_MESSAGE, reply_markup=None)
        await callback.message.answer(GREET_MESSAGE, reply_markup=keyboard)
        return
        
    # Получаем подписки для выбранного типа
    grouped_subscriptions = user_subscriptions_data.get(callback.from_user.id, {})
    subscriptions_for_type = grouped_subscriptions.get(selected_type, [])
    
    # Форматируем подписки с расчетом экономии
    monthly_subscription = next((s for s in subscriptions_for_type if s.get('period', 1) == 1), None)
    formatted_subscriptions = []
    
    for subscription in subscriptions_for_type:
        formatted_sub = format_subscription_with_savings(subscription, monthly_subscription)
        formatted_subscriptions.append(formatted_sub)
    
    # Создаем клавиатуру с периодами
    keyboard = get_subscription_periods_keyboard(selected_type, formatted_subscriptions)
    
    # Формируем сообщение с описанием типа подписки
    type_descriptions = {
        "Дневная карта": "💼 <b>Дневная карта</b>\n\nПосещение с 7:00 до 17:00, тренажёрный зал и кардио-зона.",
        "Полный день": "🌟 <b>Полный день</b>\n\nБезлимитное посещение в любое время, тренажёрный зал и кардио-зона.",
        "Все включено": "🏆 <b>Все включено</b>\n\nБезлимитное посещение, все групповые программы, спа-зона и скалодром."
    }
    
    description = type_descriptions.get(selected_type, f"<b>{selected_type}</b>")
    description += "\n\n💰 Выберите период подписки:"
    
    await callback.message.edit_text(description, reply_markup=None)
    await callback.message.answer(description, reply_markup=keyboard)


@router.message(lambda message: message.text not in ["Личный кабинет", "Подписки", "Задать вопрос", "🏠 В главное меню", "❌ Завершить диалог", "🧪 Тестовая подписка", "💼 Дневная карта", "🌟 Полный день", "🏆 Все включено", "🔙 Назад к типам подписок"] and not (message.text and "мес. —" in message.text))
async def subscription_variant_handler(message: Message, state: FSMContext):
    """Обработка старого выбора варианта подписки (fallback)"""
    logger.info(f"🔍 subscription_variant_handler (fallback) вызван! user_id={message.from_user.id}, text='{message.text}'")
    
    # Возвращаем к новому интерфейсу
    keyboard = get_subscription_types_keyboard()
    await message.answer("Используйте новый интерфейс подписок:", reply_markup=keyboard)


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
        
        # Безопасное преобразование в int
        try:
            fee_price_int = int(sub_fee_price) if sub_fee_price and str(sub_fee_price).strip() else 0
            sub_price_int = int(sub_price) if sub_price else 0
            total_price = fee_price_int + sub_price_int
        except (ValueError, TypeError):
            fee_price_int = 0
            sub_price_int = int(sub_price) if sub_price else 0
            total_price = sub_price_int

        pay_message = f"""
💳 <b>Оформление подписки</b>

Вы выбрали: <b>{sub_name}</b>

💰 К оплате:"""
        
        # Добавляем fee только если есть
        if fee_price_int > 0:
            pay_message += f"\n• {sub_fee_title}: {fee_price_int} ₽ (разово)"
        
        pay_message += f"""
• Абонемент на месяц: {sub_price_int} ₽
———————————————————
ИТОГО: {total_price} ₽

⬇️ Нажмите на кнопку ниже, чтобы оплатить:
"""

        if not user_token:
            await callback.message.answer("❌ Ошибка при получении ссылки на оплату. Пожалуйста, попробуйте позже.", reply_markup=main_menu())
        else:
            fitness_request = FitnessSubscriptionRequest(user_token=user_token)
            
            # Передаем fee_id только если он есть
            if sub_fee_id and sub_fee_id.strip():
                url = await fitness_request.get_payment_link(
                    subscription_id=sub_id,
                    fee_id=sub_fee_id,
                )
            else:
                url = await fitness_request.get_payment_link(
                    subscription_id=sub_id,
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

