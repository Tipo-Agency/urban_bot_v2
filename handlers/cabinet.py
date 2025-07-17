import logging
from aiogram import Router, F
from aiogram.types import Message
from db import get_user_token_by_user_id
from api.requests import FitnessSubscriptionRequest
from keyboards import get_cabinet_keyboard
from datetime import datetime

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "Личный кабинет")
async def cabinet_handler(message: Message):
    user_id = message.from_user.id
    logger.info(f"👤 Запрос личного кабинета от пользователя {user_id}")
    
    user_data = get_user_token_by_user_id(user_id)
    user_token = user_data.get('user_token') if user_data else None

    if not user_token:
        logger.warning(f"⚠️ Попытка доступа к личному кабинету без авторизации: {user_id}")
        await message.answer("❌ Вы еще не авторизованы в системе.")
        return

    # информация о пользователе
    fitness_request = FitnessSubscriptionRequest(user_token=user_token)
    client_info = await fitness_request.get_client()

    if not client_info or not client_info.get("result"):
        logger.error(f"❌ Не удалось получить данные профиля для пользователя {user_id}")
        await message.answer("❌ Не удалось получить данные профиля. Попробуйте позже.")
        return

    data = client_info.get("data", {})

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

    #информация о подписке
    subscriptions_data = await fitness_request.get_user_subscriptions()
    first_subscription = subscriptions_data.get("subscriptions", [{}])[0]

    subsctiption_id = first_subscription.get("item_id", "")
    title = first_subscription.get("title")
    status = first_subscription.get("status")
    active_date = first_subscription.get("active_date", "")
    end_date = first_subscription.get("end_date", "")
    price = first_subscription.get("recurrent_details", {}).get("payment_amount", "")

    if active_date and end_date:
        # Преобразуем строки в datetime-объекты
        active = datetime.strptime(active_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Считаем, сколько дней осталось
        days_left = (end - datetime.today().date()).days
    

    msg = (
        "👤 <b>Личный кабинет</b>\n\n"
        f"<b>ФИО:</b> {fio}\n"
        f"<b>Телефон:</b> {phone}\n"
        f"<b>Email:</b> {email}\n"
        f"<b>Дата рождения:</b> {birthday}\n"
        f"<b>Пол:</b> {sex_str}\n"
        f"<b>Клуб:</b> {club_name}\n"
        f"<b>Теги:</b> {tags}\n\n"
    )
    if promo_code:
        msg += f"<b>Промокоды:</b> {promo_code}\n\n"

    if first_subscription:
        msg += (
            f"💳 <b>Текущий тариф:</b> {title}\n"
            f"<b>Начало:</b> {active_date}\n"
            f"<b>Окончание:</b> {end_date}\n"
            f"<b>Осталось:</b> {days_left} дней\n"
            f"<b>Цена:</b> {price} ₽/мес\n"
            f"<b>Статус:</b> {status}\n"
        )

    await message.answer(msg, reply_markup=get_cabinet_keyboard())