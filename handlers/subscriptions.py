# from aiogram import Router, F
# from aiogram.types import Message, CallbackQuery
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
# import uuid
# import re

# from db import create_or_update_user, get_user_by_chat_id
# from messages import GREET_MESSAGE, SELECT_ANOTHER, SUBSCRIPTION_VARIANTS, get_pay_message
# from config import BASE_URL
# from keyboards import main_menu

# router = Router()

# class SubscriptionStates(StatesGroup):
#     awaiting_fio = State()
#     awaiting_phone = State()
#     processing_payment = State()

# def get_subscription_keyboard():
#     """Создает клавиатуру с вариантами подписок"""
#     keyboard = []
#     for variant in SUBSCRIPTION_VARIANTS:
#         keyboard.append([KeyboardButton(text=variant['description'])])
    
#     # Добавляем кнопку возврата в главное меню
#     keyboard.append([KeyboardButton(text="🏠 В главное меню")])
    
#     return ReplyKeyboardMarkup(
#         keyboard=keyboard,
#         resize_keyboard=True,
#         one_time_keyboard=True
#     )

# def get_payment_keyboard(user_id: str):
#     """Создает инлайн клавиатуру для оплаты"""
#     url = f"{BASE_URL}/payment?token={user_id}"
    
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(text="💳 Оплатить", url=url)],
#             [InlineKeyboardButton(text="Выбрать другой тариф", callback_data="select_another")],
#             [InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main")]
#         ]
#     )

# def get_profile_keyboard():
#     """Создает инлайн клавиатуру для личного кабинета"""
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(text="❌ Отменить подписку", callback_data="cancel_subscription")],
#             [InlineKeyboardButton(text="🔄 Изменить тариф", callback_data="change_subscription")],
#             [InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main")]
#         ]
#     )

# @router.message(F.text == "🏠 В главное меню")
# async def back_to_main_menu_handler(message: Message, state: FSMContext):
#     """Обработчик возврата в главное меню через текстовую кнопку"""
#     await state.clear()
    
#     greeting_text = f"""
# 🏠 <b>Главное меню</b>

# Добро пожаловать, <b>{message.from_user.first_name}</b>!
# Выберите, что вас интересует:
# """
    
#     await message.answer(greeting_text, reply_markup=main_menu())

# @router.callback_query(F.data == "back_to_main")
# async def back_to_main_callback_handler(callback: CallbackQuery, state: FSMContext):
#     """Обработчик возврата в главное меню через callback кнопку"""
#     await callback.answer()
#     await state.clear()
    
#     greeting_text = f"""
# 🏠 <b>Главное меню</b>

# Добро пожаловать, <b>{callback.from_user.first_name}</b>!
# Выберите, что вас интересует:
# """
    
#     await callback.message.answer(greeting_text, reply_markup=main_menu())
#     await callback.message.delete()

# @router.message(F.text == "Личный кабинет")
# async def profile_handler(message: Message):
#     """Обработчик личного кабинета"""
#     user_data = get_user_by_chat_id(message.chat.id)
    
#     if not user_data or not user_data.get('fio'):
#         await message.answer("""
# ❌ Вы еще не зарегистрированы в системе.

# Для начала оформите подписку через раздел "Подписки".
# """, reply_markup=InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [InlineKeyboardButton(text="💳 Оформить подписку", callback_data="go_to_subscriptions")],
#                 [InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main")]
#             ]
#         ))
#         return
    
#     # Находим информацию о тарифе
#     sub_type = user_data.get('sub_type', 1)
#     subscription = next((s for s in SUBSCRIPTION_VARIANTS if s['id'] == sub_type), SUBSCRIPTION_VARIANTS[0])
    
#     # Получаем описание тарифа без первой строки (цены)
#     description_lines = subscription['description'].split('\n')
#     tariff_description = description_lines[1] if len(description_lines) > 1 else ''
    
#     profile_text = f"""
# 👤 <b>Личный кабинет</b>

# 📋 <b>Ваши данные:</b>
# • ФИО: {user_data['fio']}
# • Телефон: {user_data['phone']}

# 💳 <b>Текущий тариф:</b>
# • {subscription['title']} — {subscription['price']} ₽/мес
# • {tariff_description}

# ℹ️ Управление подпиской:
# """
    
#     await message.answer(profile_text, reply_markup=get_profile_keyboard())

# @router.callback_query(F.data == "go_to_subscriptions")
# async def go_to_subscriptions_handler(callback: CallbackQuery, state: FSMContext):
#     """Переход к подпискам из личного кабинета"""
#     await callback.answer()
#     await state.clear()
    
#     await callback.message.answer(GREET_MESSAGE, reply_markup=get_subscription_keyboard())
#     await callback.message.delete()

# @router.message(F.text == "Подписки")
# async def subscriptions_handler(message: Message, state: FSMContext):
#     await state.clear()
#     await message.answer(GREET_MESSAGE, reply_markup=get_subscription_keyboard())

# @router.message(F.text.in_([variant['description'] for variant in SUBSCRIPTION_VARIANTS]))
# async def subscription_variant_handler(message: Message, state: FSMContext):
#     """Обработка выбора варианта подписки"""
#     # Находим выбранный тариф
#     selected_variant = None
#     for variant in SUBSCRIPTION_VARIANTS:
#         if variant['description'] == message.text.strip():
#             selected_variant = variant
#             break
    
#     if not selected_variant:
#         return
    
#     # Сохраняем выбранный тариф в состоянии
#     await state.update_data(sub_type=selected_variant['id'])
    
#     # Проверяем, есть ли пользователь в базе
#     user_data = get_user_by_chat_id(message.chat.id)
    
#     if user_data and user_data.get('fio') and user_data.get('phone'):
#         # Пользователь уже есть, сразу создаем ссылку на оплату
#         user_id = user_data['id']
        
#         # Обновляем тип подписки
#         create_or_update_user(
#             user_id=user_id,
#             chat_id=message.chat.id,
#             fio=user_data['fio'],
#             phone=user_data['phone'],
#             sub_type=selected_variant['id']
#         )
        
#         pay_message = get_pay_message(selected_variant['title'], selected_variant['price'])
        
#         await message.answer(
#             f"Тариф изменен на {selected_variant['title']}", 
#             reply_markup=ReplyKeyboardRemove()
#         )
#         await message.answer(pay_message, reply_markup=get_payment_keyboard(user_id))
#     else:
#         # Новый пользователь, запрашиваем ФИО
#         await state.set_state(SubscriptionStates.awaiting_fio)
#         cancel_keyboard = InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_main")]
#             ]
#         )
#         await message.answer("Введите ваше ФИО:", reply_markup=cancel_keyboard)

# @router.message(SubscriptionStates.awaiting_fio)
# async def process_fio(message: Message, state: FSMContext):
#     """Обработка ввода ФИО"""
#     fio = message.text.strip()
#     await state.update_data(fio=fio)
#     await state.set_state(SubscriptionStates.awaiting_phone)
    
#     cancel_keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_main")]
#         ]
#     )
#     await message.answer("Введите ваш номер телефона (в формате +7XXXXXXXXXX):", reply_markup=cancel_keyboard)

# @router.message(SubscriptionStates.awaiting_phone)
# async def process_phone(message: Message, state: FSMContext):
#     """Обработка ввода телефона"""
#     phone = message.text.strip()
    
#     # Проверяем формат телефона
#     phone_regex = r'^\+7\d{10}$'
#     if not re.match(phone_regex, phone):
#         cancel_keyboard = InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_main")]
#             ]
#         )
#         await message.answer("Неверный формат номера. Попробуйте снова (например, +71234567890).", 
#                            reply_markup=cancel_keyboard)
#         return
    
#     # Получаем данные из состояния
#     data = await state.get_data()
#     fio = data.get('fio')
#     sub_type = data.get('sub_type', 1)
    
#     # Проверяем, есть ли пользователь в базе
#     existing_user = get_user_by_chat_id(message.chat.id)
#     user_id = existing_user['id'] if existing_user else str(uuid.uuid1())
    
#     # Сохраняем/обновляем пользователя в базе
#     create_or_update_user(
#         user_id=user_id,
#         chat_id=message.chat.id,
#         fio=fio,
#         phone=phone,
#         sub_type=sub_type
#     )
    
#     # Находим выбранный тариф
#     selected_variant = next((v for v in SUBSCRIPTION_VARIANTS if v['id'] == sub_type), SUBSCRIPTION_VARIANTS[0])
    
#     # Генерируем сообщение для оплаты
#     pay_message = get_pay_message(selected_variant['title'], selected_variant['price'])
    
#     await state.set_state(SubscriptionStates.processing_payment)
#     await message.answer(pay_message, reply_markup=get_payment_keyboard(user_id))

# @router.callback_query(F.data == "select_another")
# async def select_another_handler(callback: CallbackQuery, state: FSMContext):
#     """Обработка кнопки 'Выбрать другой тариф'"""
#     await callback.answer()
#     await state.clear()
    
#     await callback.message.answer(SELECT_ANOTHER, reply_markup=get_subscription_keyboard())
#     await callback.message.delete()

# @router.callback_query(F.data == "cancel_subscription")
# async def cancel_subscription_handler(callback: CallbackQuery):
#     """Обработка отмены подписки"""
#     await callback.answer()
    
#     cancel_text = """
# ❌ <b>Отмена подписки</b>

# Для отмены подписки свяжитесь с менеджером клуба:
# 📞 Телефон: +7 (xxx) xxx-xx-xx
# 💬 Telegram: @manager_username

# Либо обратитесь в отдел продаж при посещении клуба.

# ⚠️ <b>Важно:</b> отмена подписки вступает в силу с начала следующего расчетного периода.
# """
    
#     back_keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main")]
#         ]
#     )
    
#     await callback.message.answer(cancel_text, reply_markup=back_keyboard)

# @router.callback_query(F.data == "change_subscription")
# async def change_subscription_handler(callback: CallbackQuery, state: FSMContext):
#     """Обработка изменения тарифа"""
#     await callback.answer()
#     await state.clear()
    
#     await callback.message.answer(
#         "Выберите новый тариф:", 
#         reply_markup=get_subscription_keyboard()
#     )
#     await callback.message.delete()


