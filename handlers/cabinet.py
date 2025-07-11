from aiogram import Router, F
from aiogram.types import Message
from db import get_user_token_by_user_id
from api.requests import FitnessAuthRequest
from keyboards import get_cabinet_keyboard

router = Router()


@router.message(F.text == "Личный кабинет")
async def cabinet_handler(message: Message):
    user_data = get_user_token_by_user_id(message.from_user.id)
    user_token = user_data.get('user_token') if user_data else None

    if not user_token:
        await message.answer("❌ Вы еще не авторизованы в системе.")
        return

    client_info = await FitnessAuthRequest(user_token=user_token).get_client()

    if not client_info or not client_info.get("result"):
        await message.answer("❌ Не удалось получить данные профиля. Попробуйте позже.")
        return

    data = client_info.get("data", {})

    # Формируем красивое сообщение
    fio = f"{data.get('last_name', '')} {data.get('name', '')} {data.get('second_name', '')}".strip()
    email = data.get("email", "—")
    phone = data.get("phone", "—")
    birthday = data.get("birthday", "—")
    sex = data.get("sex")
    sex_str = "Мужской" if sex == 1 else ("Женский" if sex == 2 else "—")
    club = data.get("club", {})
    club_name = club.get("name", "—")
    tags = ", ".join([tag.get("title", "") for tag in data.get("tags", [])]) or "—"
    promo_code = ", ".join([promo.get("code", "") for promo in data.get("promo_codes", [])]) or "—"


    # В текущем коде есть потенциальная ошибка в использовании тернарного оператора внутри f-строк.
    # Конструкция:
    # f"<b>Промокоды:</b> {promo_code}\n\n" if promo_code else ""
    # приведёт к тому, что если promo_code пустой, то ВСЁ остальное после этого (начиная с тарифа) не попадёт в итоговую строку.
    # Это связано с тем, что тернарный оператор применяется ко всей оставшейся части скобок, а не только к одной строке.
    # Исправленный вариант — вынести блок с промокодами отдельно:

    msg = (
        "👤 <b>Личный кабинет</b>\n\n"
        f"<b>ФИО:</b> {fio}\n"
        f"<b>Телефон:</b> {phone}\n"
        f"<b>Email:</b> {email}\n"
        f"<b>Дата рождения:</b> {birthday}\n"
        f"<b>Пол:</b> {sex_str}\n"
        f"<b>Клуб:</b> {club_name}\n"
        f"<b>Теги:</b> {tags}\n"
    )
    if promo_code:
        msg += f"<b>Промокоды:</b> {promo_code}\n\n"
    else:
        msg += "\n"
    msg += (
        f"💳 <b>Текущий тариф:</b> SmartFit\n"
        f"<b>Начало:</b> 10.07.2025\n"
        f"<b>Окончание:</b> 10.08.2025\n"
        f"<b>Осталось:</b> 20 дней\n"
        f"<b>Цена:</b> 1000 ₽/мес\n"
        f"<b>Статус:</b> Активен\n"
    )

    await message.answer(msg, reply_markup=get_cabinet_keyboard())