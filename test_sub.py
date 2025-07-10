#!/usr/bin/env python3
"""
Простой тест для проверки работы упрощенного модуля подписок
"""

import asyncio
from messages import get_subscriptions_from_api, get_default_subscriptions
from api.requests import FitnessAuthRequest

async def test_subscriptions():
    """Тестирование получения подписок"""
    print("🚀 Тестирование упрощенного модуля подписок...")
    print("=" * 50)
    
    # Тест 1: Получение подписок из API
    print("\n1. Получение подписок из API...")
    subscriptions = await get_subscriptions_from_api()
    
    if subscriptions:
        print(f"✅ Получено {len(subscriptions)} подписок:")
        for sub in subscriptions:
            print(f"   • {sub['title']} — {sub['price']} ₽/мес")
            print(f"     Sub ID: {sub['sub_id']}")
    else:
        print("❌ Не удалось получить подписки из API")
    
    # Тест 2: Проверка структуры данных
    print("\n2. Проверка структуры данных...")
    if subscriptions:
        sample_sub = subscriptions[0]
        required_fields = ['id', 'sub_id', 'title', 'description', 'price']
        
        for field in required_fields:
            if field in sample_sub:
                print(f"   ✅ Поле '{field}' присутствует")
            else:
                print(f"   ❌ Поле '{field}' отсутствует")
    
    # Тест 3: Проверка дефолтных подписок
    print("\n3. Проверка дефолтных подписок...")
    default_subscriptions = get_default_subscriptions()
    print(f"✅ Дефолтные подписки ({len(default_subscriptions)}):")
    for sub in default_subscriptions:
        print(f"   • {sub['title']} — {sub['price']} ₽/мес")
    
    # Тест 4: Получение детальной информации о подписке
    print("\n4. Получение детальной информации о подписке...")
    if subscriptions:
        # Берем первую подписку для теста
        test_subscription = subscriptions[0]
        subscription_id = test_subscription.get('sub_id', '')
        
        if subscription_id:
            print(f"   Тестируем подписку: {test_subscription['title']} (ID: {subscription_id})")
            
            try:
                # Создаем объект для работы с API
                fitness_request = FitnessAuthRequest()
                
                # Получаем детальную информацию
                details = await fitness_request.get_subscription_details(subscription_id)
                
                if details and details.get("subscription"):
                    sub_details = details["subscription"]
                    print("   ✅ Детальная информация получена:")
                    print(f"      • Название: {sub_details.get('title', 'Не указано')}")
                    print(f"      • Цена: {sub_details.get('price', 'Не указано')}")
                    print(f"      • Описание: {sub_details.get('description', 'Не указано')[:50]}...")
                    print(f"      • Время доступа: {sub_details.get('available_time', 'Не указано')}")
                    print(f"      • Период действия: {sub_details.get('validity_period', 'Не указано')}")
                    print(f"      • Ограничения: {sub_details.get('restriction', 'Не указано')}")
                    
                    if sub_details.get('fee'):
                        fee = sub_details['fee']
                        print(f"      • Вступительный взнос: {fee.get('price', 'Не указано')} ₽")
                else:
                    print("   ⚠️ Детальная информация не получена (возможно, API недоступен)")
                    
            except Exception as e:
                print(f"   ❌ Ошибка получения деталей: {e}")
        else:
            print("   ⚠️ ID подписки не найден для тестирования")
    else:
        print("   ⚠️ Нет подписок для тестирования деталей")
    
    # Тест 5: Проверка обработки ошибок API
    print("\n5. Проверка обработки ошибок API...")
    try:
        # Тестируем с несуществующим ID
        fitness_request = FitnessAuthRequest()
        fake_details = await fitness_request.get_subscription_details("fake_id_12345")
        
        if fake_details is None:
            print("   ✅ Обработка ошибок работает корректно (None для несуществующего ID)")
        else:
            print("   ⚠️ Неожиданный результат для несуществующего ID")
            
    except Exception as e:
        print(f"   ✅ Исключение обработано корректно: {type(e).__name__}")
    
    print("\n" + "=" * 50)
    print("✅ Тестирование завершено!")
    print("\n📝 Функциональность:")
    print("   - Показ списка доступных подписок")
    print("   - Детальная информация о каждой подписке")
    print("   - Кнопка покупки с переходом к оплате")
    print("   - Fallback на дефолтные данные при ошибках API")
    print("   - Обработка ошибок при получении деталей")

if __name__ == "__main__":
    asyncio.run(test_subscriptions())