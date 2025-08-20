GREET_MESSAGE = """
🏋️ Добро пожаловать в клуб!  

Оформите подписку онлайн и начните тренироваться уже сегодня 💪  
Перед оплатой ознакомьтесь с условиями:

🔹 Вступительный взнос — 3000 ₽ (разовый, оплачивается при первой покупке)  
🔹 Далее — ежемесячное списание выбранного тарифа  
🔹 Подписку можно приостановить в любой момент  

💳 Выберите тип клубной карты:
"""

SELECT_ANOTHER = """
💳 Выберите тип клубной карты

🔹 Вступительный взнос — 3000 ₽ (разовый, оплачивается при первой покупке)  
🔹 Далее — ежемесячное списание выбранного тарифа  
🔹 Подписку можно приостановить в любой момент  
"""

START_PRICE = 3000

def get_pay_message(title: str, price: int) -> str:
    """Генерирует сообщение для оплаты"""
    return f"""
📝 Вы выбрали тариф {title} 

💳 К оплате:
• Вступительный взнос: {START_PRICE} ₽ (разово)
• Абонемент на месяц: {price} ₽
—————————————
ИТОГО: {START_PRICE + price} ₽

⬇️ Нажмите на кнопку ниже, чтобы оплатить:
"""

import logging

logger = logging.getLogger(__name__)

# Функция для получения реальных подписок из API
async def get_subscriptions_from_api(user_token: str = None):
    """Получает реальные данные подписок из API или использует переданные данные"""
    try:
        # Для тестирования можно вернуть данные из переданного JSON
        # Но лучше все же получать их из API
        from api.requests import FitnessSubscriptionRequest
        
        fitness_request = FitnessSubscriptionRequest(user_token)
        result = await fitness_request.get_subscriptions()

        logger.debug(f"🔍 Результат get_subscriptions: {result}")
        if result and result.get("subscriptions"):
            # Преобразуем данные API в новый формат
            subscriptions = []
            for i, sub in enumerate(result["subscriptions"], 1):
                # Извлекаем цену из строки (предполагаем формат "XXXX ₽")
                price_str = sub.get("price", "0")
                price = int(''.join(filter(str.isdigit, price_str))) if price_str else 0
                
                # Формируем описание
                available_time = sub.get("available_time", "")
                description = sub.get("description", "")
                if not description:
                    description = f"{sub.get('title', 'Тариф')} — {price} ₽"
                    if available_time:
                        description += f"\n{available_time}"
                
                # Добавляем недостающие поля для совместимости
                subscription_data = {
                    "id": i,
                    "sub_id": sub.get("id", ""),  # Сохраняем оригинальный ID из API
                    "title": sub.get("title", "Тариф"),
                    "description": description,
                    "price": price,
                    "available_time": available_time,
                    "fee": {
                        "id": sub.get("fee", {}).get("id", ""),
                        "title": sub.get("fee", {}).get("title", ""),
                        "price": sub.get("fee", {}).get("price", ""),
                    },
                    "validity": sub.get("validity", {}),
                    "services": sub.get("services", [])
                }
                
                subscriptions.append(subscription_data)
            
            logger.debug(f"✅ Получено {len(subscriptions)} подписок из API")
            return subscriptions
        else:
            # Возвращаем дефолтные данные если API недоступен
            logger.warning("⚠️ API недоступен, используем тестовые подписки из JSON")
            return get_test_subscriptions_from_json()
            
    except Exception as e:
        logger.error(f"❌ Ошибка получения подписок из API: {e}")
        # Возвращаем тестовые данные при ошибке
        return get_test_subscriptions_from_json()


def get_test_subscriptions_from_json():
    """Возвращает тестовые данные подписок из переданного JSON"""
    return [
        {
            "id": 1,
            "sub_id": "13d7c685-737d-11f0-bbf7-96ba5d0233b2",
            "title": "Все включено 12 месяцев",
            "description": "Безлимитное посещение, все групповые программы, спа-зона и скалодром.",
            "price": 23900,
            "available_time": "Часы посещений ограничены: ",
            "fee": {"id": "", "title": "", "price": ""}
        },
        {
            "id": 2,
            "sub_id": "7f2e7462-737c-11f0-bbf7-96ba5d0233b2",
            "title": "Все включено 2 400 р. / мес.",
            "description": "Безлимитное посещение, все групповые программы, спа-зона и скалодром.",
            "price": 2400,
            "available_time": "",
            "fee": {"id": "1033dc61-2fc7-11f0-bbd0-99fe2db82e7a", "title": "Стартовый взнос", "price": "3000"}
        },
        {
            "id": 3,
            "sub_id": "cf98e44b-737c-11f0-bbf7-96ba5d0233b2",
            "title": "Все включено 6 месяцев",
            "description": "Безлимитное посещение, все групповые программы, спа-зона и скалодром.",
            "price": 13900,
            "available_time": "",
            "fee": {"id": "", "title": "", "price": ""}
        },
        {
            "id": 4,
            "sub_id": "8d7cd24b-737f-11f0-bbf7-96ba5d0233b2",
            "title": "Дневная карта 1 300 р. / мес.",
            "description": "Посещение с 7:00 до 17:00, тренажёрный зал и кардио-зона.",
            "price": 1300,
            "available_time": "",
            "fee": {"id": "1033dc61-2fc7-11f0-bbd0-99fe2db82e7a", "title": "Стартовый взнос", "price": "3000"}
        },
        {
            "id": 5,
            "sub_id": "c63ba007-7382-11f0-bbf7-96ba5d0233b2",
            "title": "Дневная карта 12 месяцев",
            "description": "Посещение с 7:00 до 17:00, тренажёрный зал и кардио-зона.",
            "price": 14900,
            "available_time": "",
            "fee": {"id": "", "title": "", "price": ""}
        },
        {
            "id": 6,
            "sub_id": "c13dee18-737f-11f0-bbf7-96ba5d0233b2",
            "title": "Дневная карта 6 месяцев",
            "description": "Посещение с 7:00 до 17:00, тренажёрный зал и кардио-зона.",
            "price": 8900,
            "available_time": "",
            "fee": {"id": "", "title": "", "price": ""}
        },
        {
            "id": 7,
            "sub_id": "fed5ab4c-7382-11f0-bbf7-96ba5d0233b2",
            "title": "Полный день 1 700 р. / мес.",
            "description": "Безлимитное посещение в любое время, тренажёрный зал и кардио-зона.",
            "price": 1700,
            "available_time": "",
            "fee": {"id": "1033dc61-2fc7-11f0-bbd0-99fe2db82e7a", "title": "Стартовый взнос", "price": "3000"}
        },
        {
            "id": 8,
            "sub_id": "6c627e48-7383-11f0-bbf7-96ba5d0233b2",
            "title": "Полный день 12 месяцев",
            "description": "Безлимитное посещение в любое время, тренажёрный зал и кардио-зона.",
            "price": 17900,
            "available_time": "",
            "fee": {"id": "", "title": "", "price": ""}
        },
        {
            "id": 9,
            "sub_id": "348f7a39-7383-11f0-bbf7-96ba5d0233b2",
            "title": "Полный день 6 месяцев",
            "description": "Безлимитное посещение в любое время, тренажёрный зал и кардио-зона.",
            "price": 10900,
            "available_time": "",
            "fee": {"id": "", "title": "", "price": ""}
        }
    ]


def group_subscriptions_by_type(subscriptions_data):
    """Группирует подписки по типам и сортирует по длительности"""
    grouped = {}
    
    for subscription in subscriptions_data:
        title = subscription.get("title", "")
        
        # Определяем тип подписки по названию
        if "Тест" in title:
            subscription_type = "Тест"
        elif "Дневная карта" in title:
            subscription_type = "Дневная карта"
        elif "Полный день" in title:
            subscription_type = "Полный день"
        elif "Все включено" in title:
            subscription_type = "Все включено"
        else:
            subscription_type = "Другое"
        
        # Определяем период подписки
        if "12 месяц" in title:
            period = 12
        elif "6 месяц" in title:
            period = 6
        else:
            period = 1
        
        # Добавляем период в данные подписки
        subscription["period"] = period
        subscription["type"] = subscription_type
        
        if subscription_type not in grouped:
            grouped[subscription_type] = []
        
        grouped[subscription_type].append(subscription)
    
    # Сортируем каждую группу по периоду (1, 6, 12 месяцев)
    for group_type in grouped:
        if group_type != "Тест":  # Тестовая подписка не сортируется по периоду
            grouped[group_type].sort(key=lambda x: x.get("period", 1))
    
    return grouped


def calculate_savings_percentage(monthly_price, multi_month_price, period):
    """Вычисляет процент экономии при покупке подписки на несколько месяцев"""
    if not monthly_price or not multi_month_price or period <= 1:
        return 0
    
    # Общая стоимость при ежемесячной оплате
    total_monthly_cost = monthly_price * period
    
    # Экономия в рублях
    savings = total_monthly_cost - multi_month_price
    
    # Процент экономии
    if total_monthly_cost > 0:
        savings_percentage = (savings / total_monthly_cost) * 100
        return round(savings_percentage)
    
    return 0


def format_subscription_with_savings(subscription, monthly_subscription=None):
    """Форматирует подписку с отображением экономии"""
    title = subscription.get("title", "")
    price = subscription.get("price", 0)
    period = subscription.get("period", 1)
    description = subscription.get("description", "")
    
    # Если это подписка на 6 или 12 месяцев, вычисляем экономию
    if period > 1 and monthly_subscription:
        monthly_price = monthly_subscription.get("price", 0)
        if monthly_price > 0:
            savings_percent = calculate_savings_percentage(monthly_price, price, period)
            if savings_percent > 0:
                title += f" 🔥 ЭКОНОМИЯ {savings_percent}%"
    
    return {
        "title": title,
        "price": price,
        "period": period,
        "description": description,
        "id": subscription.get("id"),
        "sub_id": subscription.get("sub_id"),
        "fee": subscription.get("fee", {}),
        "type": subscription.get("type", "")
    }

def get_default_subscriptions():
    """Возвращает дефолтные данные подписок"""
    return [
        {
            "id": 1,
            "sub_id": "default_1",
            "title": "SmartFit",
            "description": "SmartFit — 1300 ₽/мес\nДоступ: 07:00–17:30, 20:30–23:30",
            "price": 1300,
        },
        {
            "id": 2,
            "sub_id": "default_2", 
            "title": "FitFlow",
            "description": "FitFlow — 1700 ₽/мес\nБезлимитный доступ в любое время",
            "price": 1700,
        },
        {
            "id": 3,
            "sub_id": "default_3",
            "title": "ProFit",
            "description": "ProFit — 2400 ₽/мес\nБезлимит + групповые программы",
            "price": 2400,
        },
    ]

# Дефолтные варианты подписок (используются как fallback)
SUBSCRIPTION_VARIANTS = get_default_subscriptions()

MASSIVE_SUCCESS = """
🎉 Отлично! Подписка успешно оформлена!

Теперь подойдите в отдел продаж клуба — вас зарегистрируют в системе.  
Вы уже можете начать посещать клуб хоть сегодня — доступ активирован 🔓

До встречи в зале! 🏋️🔥
""" 