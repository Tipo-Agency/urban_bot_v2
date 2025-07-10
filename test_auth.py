#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы авторизации
"""

import asyncio
from api.requests import FitnessRequest
from db import init_db, create_or_update_user, get_user_token_by_user_id, delete_user

async def test_fitness_request():
    """Тестирование API запросов"""
    print("🧪 Тестирование FitnessRequest API...")
    
    fitness_request = FitnessRequest()
    
    # Тест 1: Отправка кода подтверждения
    print("\n1. Тестирование отправки кода подтверждения...")
    phone = 79242231931  # Замените на реальный номер для тестирования
    result = await fitness_request.confirm_phone(phone, "")
    
    if result:
        print(f"✅ Код подтверждения отправлен успешно")
        print(f"Ответ API: {result}")
    else:
        print("❌ Ошибка при отправке кода подтверждения")
        return
    
    # Тест 2: Проверка кода (нужно ввести реальный код)
    print("\n2. Тестирование проверки кода...")
    code = input("Введите код из WhatsApp: ").strip()
    
    if not code:
        print("❌ Код не введен")
        return
    
    result = await fitness_request.confirm_phone(phone, code)
    
    if result and result.get('password_token'):
        print(f"✅ Код подтвержден успешно")
        print(f"Password token: {result['password_token']}")
        
        # Тест 3: Создание пользователя
        print("\n3. Тестирование создания пользователя...")
        
        password = "test123456"
        last_name = "Тестов"
        name = "Пользователь"
        second_name = ""
        
        user_result = await fitness_request.set_password(
            password_token=result['password_token'],
            password=password,
            phone=phone,
            last_name=last_name,
            name=name,
            second_name=second_name
        )
        
        if user_result:
            print(f"✅ Пользователь создан успешно")
            print(f"Ответ API: {user_result}")
        else:
            print("❌ Ошибка при создании пользователя")
    else:
        print("❌ Неверный код подтверждения")

def test_database():
    """Тестирование базы данных"""
    print("\n🗄️ Тестирование базы данных...")
    
    # Инициализация БД
    init_db()
    print("✅ База данных инициализирована")
    
    # Тест создания пользователя
    test_user_id = 12345
    test_token = "test_token_123"
    
    create_or_update_user(test_user_id, test_token)
    print(f"✅ Пользователь {test_user_id} создан/обновлен")
    
    # Тест получения пользователя
    user_data = get_user_token_by_user_id(test_user_id)
    if user_data:
        print(f"✅ Пользователь найден: {user_data}")
    else:
        print("❌ Пользователь не найден")
    
    # Тест удаления пользователя
    delete_user(test_user_id)
    print(f"✅ Пользователь {test_user_id} удален")
    
    # Проверяем, что пользователь удален
    user_data = get_user_token_by_user_id(test_user_id)
    if not user_data:
        print("✅ Пользователь успешно удален")
    else:
        print("❌ Пользователь не удален")

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов авторизации...")
    
    # Тест базы данных
    # test_database()
    test_fitness_request()
    
    # Тест API (раскомментируйте для тестирования с реальным API)
    # await test_fitness_request()
    
    print("\n✅ Все тесты завершены!")

if __name__ == "__main__":
    asyncio.run(main()) 