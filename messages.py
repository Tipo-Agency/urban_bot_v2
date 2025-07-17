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

# Функция для получения реальных подписок из API
async def get_subscriptions_from_api(user_token: str = None):
    """Получает реальные данные подписок из API"""
    try:
        from api.requests import FitnessSubscriptionRequest
        
        fitness_request = FitnessSubscriptionRequest(user_token)
        result = await fitness_request.get_subscriptions()
        
        if result and result.get("subscriptions"):
            # Преобразуем данные API в формат, совместимый с текущим кодом
            subscriptions = []
            for i, sub in enumerate(result["subscriptions"], 1):
                # Извлекаем цену из строки (предполагаем формат "XXXX ₽")
                price_str = sub.get("price", "0")
                price = int(''.join(filter(str.isdigit, price_str))) if price_str else 0
                
                # Формируем описание
                available_time = sub.get("available_time", "")
                description = f"{sub.get('title', 'Тариф')} — {price} ₽/мес"
                if available_time:
                    description += f"\n{available_time}"
                
                subscriptions.append({
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
                    }
                })
            
            return subscriptions
        else:
            # Возвращаем дефолтные данные если API недоступен
            return get_default_subscriptions()
            
    except Exception as e:
        print(f"Ошибка получения подписок из API: {e}")
        # Возвращаем дефолтные данные при ошибке
        return get_default_subscriptions()

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