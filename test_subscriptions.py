#!/usr/bin/env python3

"""
Тестовый скрипт для проверки новой логики подписок
"""

import sys
sys.path.append('.')

from messages import group_subscriptions_by_type, format_subscription_with_savings, calculate_savings_percentage, get_test_subscriptions_from_json

def test_subscription_logic():
    """Тестирует логику группировки и расчета экономии"""
    print("🧪 Тестирование новой логики подписок...\n")
    
    # Получаем тестовые данные
    subscriptions = get_test_subscriptions_from_json()
    print(f"📊 Получено {len(subscriptions)} подписок")
    
    # Группируем по типам
    grouped = group_subscriptions_by_type(subscriptions)
    print(f"📊 Сгруппировано по типам: {list(grouped.keys())}")
    
    # Проверяем каждую группу
    for group_name, group_subscriptions in grouped.items():
        print(f"\n🏷️ Тип: {group_name}")
        print(f"   Количество: {len(group_subscriptions)}")
        
        # Находим месячную подписку для расчета экономии
        monthly_sub = next((s for s in group_subscriptions if s.get('period', 1) == 1), None)
        
        for sub in group_subscriptions:
            formatted = format_subscription_with_savings(sub, monthly_sub)
            period = sub.get('period', 1)
            price = sub.get('price', 0)
            
            savings_info = ""
            if period > 1 and monthly_sub:
                monthly_price = monthly_sub.get('price', 0)
                savings_percent = calculate_savings_percentage(monthly_price, price, period)
                if savings_percent > 0:
                    total_monthly = monthly_price * period
                    savings_amount = total_monthly - price
                    savings_info = f" (экономия: {savings_amount} ₽, {savings_percent}%)"
            
            print(f"   📅 {period} мес. — {price} ₽{savings_info}")
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    test_subscription_logic()