from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards import main_menu
from db import get_user_token_by_user_id, create_or_update_user
from aiogram.fsm.state import State, StatesGroup
from api.requests import FitnessRequest
import re

router = Router()

class AuthStates(StatesGroup):
    phone = State()
    code = State()
    last_name = State()
    name = State()
    second_name = State()
    password = State()

@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = get_user_token_by_user_id(user_id)
    
    # Если в БД есть user_token - пользователь авторизован
    if user_data and user_data.get('user_token'):
        await message.answer("Вы уже авторизованы!", reply_markup=main_menu)
        return
    
    # Если user_token нет - начинаем процесс регистрации
    await state.clear()
    await message.answer(
        "Добро пожаловать в бот фитнес-клуба! 🏋️‍♂️\n\n"
        "Для начала работы необходимо зарегистрироваться.\n"
        "Пожалуйста, введите ваш номер телефона в формате +7XXXXXXXXXX:"
    )
    await state.set_state(AuthStates.phone)


@router.message(AuthStates.phone, F.text)
async def process_phone_text(message: Message, state: FSMContext):
    phone = message.text.strip()
    
    # Проверяем формат номера
    if not re.match(r'^\+7\d{10}$', phone):
        await message.answer(
            "Неверный формат номера телефона.\n"
            "Пожалуйста, введите номер в формате +7XXXXXXXXXX"
        )
        return
    
    await state.update_data(phone=phone)
    
    # Отправляем запрос на подтверждение телефона
    fitness_request = FitnessRequest()
    result = await fitness_request.confirm_phone(int(phone[1:]), "")
    
    if result:
        await message.answer(
            f"Код подтверждения отправлен на номер {phone}\n"
            "Пожалуйста, введите код из WhatsApp:"
        )
        await state.set_state(AuthStates.code)
    else:
        await message.answer(
            "Ошибка при отправке кода подтверждения.\n"
            "Пожалуйста, попробуйте еще раз или обратитесь в поддержку."
        )

@router.message(AuthStates.code, F.text)
async def process_code(message: Message, state: FSMContext):
    code = message.text.strip()
    
    # Получаем номер телефона из состояния
    data = await state.get_data()
    phone = data.get('phone')
    
    if not phone:
        await message.answer("Ошибка. Начните регистрацию заново.")
        await state.clear()
        return
    
    # Проверяем код
    fitness_request = FitnessRequest()
    result = await fitness_request.confirm_phone(int(phone[1:]), code)
    
    if result and result.get('password_token'):
        await state.update_data(password_token=result['password_token'])
        await message.answer(
            "Код подтвержден! ✅\n\n"
            "Теперь необходимо заполнить ваши данные для регистрации.\n"
            "Введите вашу фамилию:"
        )
        await state.set_state(AuthStates.last_name)
    else:
        await message.answer(
            "Неверный код подтверждения.\n"
            "Пожалуйста, попробуйте еще раз:"
        )

@router.message(AuthStates.last_name, F.text)
async def process_last_name(message: Message, state: FSMContext):
    last_name = message.text.strip()
    await state.update_data(last_name=last_name)
    await message.answer("Введите ваше имя:")
    await state.set_state(AuthStates.name)

@router.message(AuthStates.name, F.text)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(name=name)
    await message.answer("Введите ваше отчество (если есть, иначе напишите '-'):")
    await state.set_state(AuthStates.second_name)

@router.message(AuthStates.second_name, F.text)
async def process_second_name(message: Message, state: FSMContext):
    second_name = message.text.strip()
    
    if second_name == "-":
        second_name = ""
    
    await state.update_data(second_name=second_name)
    await message.answer(
        "Придумайте пароль для вашего аккаунта (минимум 6 символов):"
    )
    await state.set_state(AuthStates.password)

@router.message(AuthStates.password, F.text)
async def process_password(message: Message, state: FSMContext):
    password = message.text.strip()
    
    if len(password) < 6:
        await message.answer(
            "Пароль должен содержать минимум 6 символов.\n"
            "Попробуйте еще раз:"
        )
        return
    
    # Получаем все данные из состояния
    data = await state.get_data()
    phone = data.get('phone')
    password_token = data.get('password_token')
    last_name = data.get('last_name')
    name = data.get('name')
    second_name = data.get('second_name')
    
    # Создаем пользователя через API
    fitness_request = FitnessRequest()
    result = await fitness_request.set_password(
        password_token=password_token,
        password=password,
        phone=int(phone[1:]),
        last_name=last_name,
        name=name,
        second_name=second_name
    )
    
    if result:
        # Сохраняем пользователя в базу данных
        user_id = message.from_user.id
        user_token = result.get("data", {}).get("user_token", "")
        
        if user_token:
            create_or_update_user(user_id, user_token)
            await message.answer(
                f"🎉 Регистрация успешно завершена!\n\n"
                f"Добро пожаловать, {name} {last_name}!\n"
                f"Ваш аккаунт создан и готов к использованию.",
                reply_markup=main_menu
            )
        else:
            await message.answer(
                "Регистрация завершена, но не удалось получить токен пользователя.\n"
                "Пожалуйста, обратитесь в поддержку.",
                reply_markup=main_menu
            )
    else:
        await message.answer(
            "Ошибка при создании аккаунта.\n"
            "Пожалуйста, попробуйте еще раз или обратитесь в поддержку."
        )
    
    await state.clear()