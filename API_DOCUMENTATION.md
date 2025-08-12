# API Документация для Фронтенда - Fitness Club Bot

## 🔗 Базовый URL
```
http://212.19.27.201/urban210/hs/api/v3
```

## 🔐 Аутентификация

Все запросы требуют базовую HTTP аутентификацию и API ключ:

**Заголовки для всех запросов:**
```http
Authorization: Basic <base64_encoded_credentials>
apikey: <your_api_key>
```

**Для авторизованных запросов дополнительно:**
```http
usertoken: <user_token>
```

## 📋 Список Endpoints

### 🔑 Аутентификация и Регистрация

#### 1. Получение информации о клиенте
```http
GET /client
```

**Заголовки:**
```http
apikey: <api_key>
usertoken: <user_token>
```

**Ответ (200 OK):**
```json
{
  "result": true,
  "data": {
    "id": "user_123",
    "last_name": "Иванов",
    "name": "Иван",
    "second_name": "Иванович",
    "email": "ivan@example.com",
    "phone": "79991234567",
    "birthday": "1990-01-01",
    "sex": 1,
    "club": {
      "id": "club_456",
      "name": "Urban210"
    },
    "tags": [
      {
        "id": "tag_1",
        "title": "VIP"
      }
    ],
    "promo_codes": [
      {
        "id": "promo_1",
        "code": "WELCOME2024"
      }
    ]
  }
}
```

#### 2. Аутентификация клиента
```http
POST /auth_client
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "phone": 79991234567,
  "password": "password123"
}
```

**Ответ (200 OK):**
```json
{
  "result": true,
  "data": {
    "user_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### 3. Отправка кода подтверждения
```http
POST /confirm_phone
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "phone": 79991234567,
  "auth_type": "whats_app"
}
```

**Ответ (200 OK):**
```json
{
  "result": true,
  "data": {
    "message": "Код отправлен в WhatsApp"
  }
}
```

#### 4. Подтверждение кода
```http
POST /confirm_phone
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "phone": 79991234567,
  "confirmation_code": "123456",
  "auth_type": "whats_app"
}
```

**Ответ (200 OK):**
```json
{
  "result": true,
  "data": {
    "pass_token": "pass_token_for_registration"
  }
}
```

#### 5. Регистрация нового клиента
```http
POST /reg_and_auth_client
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "phone": 79991234567,
  "password": "password123",
  "pass_token": "pass_token_from_confirm",
  "last_name": "Иванов",
  "name": "Иван",
  "second_name": "Иванович",
  "email": "ivan@example.com",
  "birth_date": "01.01.1990",
  "autopassword_to_sms": false
}
```

**Ответ (200 OK):**
```json
{
  "result": true,
  "data": {
    "user_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### 6. Установка пароля
```http
POST /password
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "pass_token": "pass_token",
  "password": "new_password",
  "phone": 79991234567,
  "last_name": "Иванов",
  "name": "Иван",
  "second_name": "Иванович"
}
```

**Ответ (200 OK):**
```json
{
  "result": true,
  "data": {
    "user_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 💳 Подписки и Платежи

#### 7. Получение списка подписок
```http
GET /price_list?type=membership&club_id=b5f85d29-6727-11e9-80cb-00155d066506
```

**Заголовки:**
```http
apikey: <api_key>
```

**Ответ (200 OK):**
```json
{
  "result": true,
  "data": [
    {
      "id": "sub_1",
      "title": "SmartFit",
      "price": "1300 ₽",
      "available_time": "07:00–17:30, 20:30–23:30",
      "fee": {
        "id": "fee_1",
        "title": "Вступительный взнос",
        "price": "3000 ₽"
      },
      "services": [
          {
              "id": "96a8ed2b-dbe2-11eb-8104-00155d06650d",
              "title": "Фитнес тестирование первичное",
              "count": 1
          },
          {
              "id": "f4905cd9-6b21-11e9-80c8-00155d06650d",
              "title": "Подарочная персональная тренировка",
              "count": 1
          }
      ],
    },
    {
      "id": "sub_2",
      "title": "FitFlow",
      "price": "1700 ₽",
      "available_time": "Безлимитный доступ",
      "fee": {
        "id": "fee_1",
        "title": "Вступительный взнос",
        "price": "3000 ₽"
      },
      "services": [
          {
              "id": "96a8ed2b-dbe2-11eb-8104-00155d06650d",
              "title": "Фитнес тестирование первичное",
              "count": 1
          },
          {
              "id": "f4905cd9-6b21-11e9-80c8-00155d06650d",
              "title": "Подарочная персональная тренировка",
              "count": 1
          }
      ],
    },
    {
      "id": "sub_3",
      "title": "ProFit",
      "price": "2400 ₽",
      "available_time": "Безлимит + групповые программы",
      "fee": {
        "id": "fee_1",
        "title": "Вступительный взнос",
        "price": "3000 ₽"
      },
      "services": [
          {
              "id": "96a8ed2b-dbe2-11eb-8104-00155d06650d",
              "title": "Фитнес тестирование первичное",
              "count": 1
          },
          {
              "id": "f4905cd9-6b21-11e9-80c8-00155d06650d",
              "title": "Подарочная персональная тренировка",
              "count": 1
          }
      ],
    }
  ]
}
```

#### 8. Получение деталей подписки
```http
GET /price_list?type=membership&club_id=b5f85d29-6727-11e9-80cb-00155d066506&service_id=sub_1
```

**Заголовки:**
```http
apikey: <api_key>
```

**Ответ (200 OK):**
```json
{
  "result": true,
  "data": [
    {
      "id": "sub_1",
      "title": "SmartFit",
      "description": "Базовый тариф с ограниченным временем доступа",
      "price": "1300 ₽",
      "available_time": "07:00–17:30, 20:30–23:30",
      "validity": {
        "validity_description": "1 месяц"
      },
      "restriction": "Доступ только в указанное время",
      "fee": {
        "id": "fee_1",
        "title": "Вступительный взнос",
        "price": "3000 ₽"
      }
    }
  ]
}
```

#### 9. Создание ссылки для оплаты
```http
POST /payment_link?service_id=sub_1
Content-Type: application/json
```

**Заголовки:**
```http
apikey: <api_key>
usertoken: <user_token>
```

**Тело запроса:**
```json
{
  "cart": [
    {
      "purchase_id": "fee_1",
      "count": 1
    },
    {
      "purchase_id": "sub_1",
      "count": 1
    }
  ]
}
```

**Ответ (200 OK):**
```json
{
  "result": true,
  "data": {
    "link": "https://widget.cloudpayments.ru/checkout/..."
  }
}
```

#### 10. Получение подписок пользователя
```http
GET /tickets?type=membership
```

**Заголовки:**
```http
apikey: <api_key>
usertoken: <user_token>
```

**Ответ (200 OK):**
```json
{
  "result": true,
  "data": [
    {
      "ticket_id": "ticket_123",
      "item_id": "sub_1",
      "type": "membership",
      "status": "active",
      "end_date": "2024-02-01",
      "status_date": "2024-01-01",
      "active_date": "2024-01-01",
      "title": "SmartFit",
      "service_list": [],
      "recurrent": true,
      "recurrent_details": {
        "payment_amount": "1300 ₽"
      },
      "available_time": "07:00–17:30, 20:30–23:30",
      "available_actions": ["freeze", "cancel"]
    }
  ]
}
```

### ⚙️ Управление Подписками

#### 11. Отмена подписки
```http
DELETE /cancellation_contract?id=recurrent_123&reason_id=d3bc2a44-9aa2-11ee-bbbe-8b03c544a7da
```

**Заголовки:**
```http
apikey: <api_key>
usertoken: <user_token>
```

**Ответ (200 OK):**
```json
{
  "result": true,
  "data": {
    "message": "Подписка успешно отменена"
  }
}
```

#### 12. Заморозка подписки
```http
POST /freeze_ticket
Content-Type: application/json
```

**Заголовки:**
```http
apikey: <api_key>
usertoken: <user_token>
```

**Тело запроса:**
```json
{
  "ticket_id": "ticket_123",
  "date": "2024-01-15",
  "count": 7
}
```

**Ответ (200 OK):**
```json
{
  "result": true,
  "data": {
    "message": "Подписка заморожена на 7 дней"
  }
}
```

#### 13. Разморозка подписки
```http
POST /unfreeze_ticket
Content-Type: application/json
```

**Заголовки:**
```http
apikey: <api_key>
usertoken: <user_token>
```

**Тело запроса:**
```json
{
  "ticket_id": "ticket_123",
  "date": "2024-01-15"
}
```

**Ответ (200 OK):**
```json
{
  "result": true,
  "data": {
    "message": "Подписка разморожена"
  }
}
```

## 🚨 Коды ошибок

### HTTP статусы
- `200` - Успешный запрос
- `400` - Неверный запрос (проверьте формат данных)
- `401` - Неавторизованный доступ (проверьте API ключ и токены)
- `404` - Ресурс не найден
- `500` - Внутренняя ошибка сервера

### Примеры ошибок

**400 Bad Request:**
```json
{
  "result": false,
  "error": "Неверный формат номера телефона"
}
```

**401 Unauthorized:**
```json
{
  "result": false,
  "error": "Неверный API ключ"
}
```

## 📝 Примеры использования для фронтенда

### JavaScript/TypeScript

#### Регистрация пользователя
```javascript
// 1. Отправка кода подтверждения
const sendCode = async (phone) => {
  const response = await fetch('http://212.19.27.201/urban210/hs/api/v3/confirm_phone', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'apikey': 'your_api_key'
    },
    body: JSON.stringify({
      phone: parseInt(phone.replace('+7', '')),
      auth_type: 'whats_app'
    })
  });
  return await response.json();
};

// 2. Подтверждение кода
const confirmCode = async (phone, code) => {
  const response = await fetch('http://212.19.27.201/urban210/hs/api/v3/confirm_phone', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'apikey': 'your_api_key'
    },
    body: JSON.stringify({
      phone: parseInt(phone.replace('+7', '')),
      confirmation_code: code,
      auth_type: 'whats_app'
    })
  });
  return await response.json();
};

// 3. Регистрация
const register = async (userData, passToken) => {
  const response = await fetch('http://212.19.27.201/urban210/hs/api/v3/reg_and_auth_client', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'apikey': 'your_api_key'
    },
    body: JSON.stringify({
      phone: parseInt(userData.phone.replace('+7', '')),
      password: userData.password,
      pass_token: passToken,
      last_name: userData.lastName,
      name: userData.firstName,
      second_name: userData.middleName || '',
      email: userData.email,
      birth_date: userData.birthDate,
      autopassword_to_sms: false
    })
  });
  return await response.json();
};
```

#### Получение подписок
```javascript
// Получение списка подписок
const getSubscriptions = async () => {
  const response = await fetch('http://212.19.27.201/urban210/hs/api/v3/price_list?type=membership&club_id=b5f85d29-6727-11e9-80cb-00155d066506', {
    headers: {
      'apikey': 'your_api_key'
    }
  });
  return await response.json();
};

// Получение деталей подписки
const getSubscriptionDetails = async (subscriptionId) => {
  const response = await fetch(`http://212.19.27.201/urban210/hs/api/v3/price_list?type=membership&club_id=b5f85d29-6727-11e9-80cb-00155d066506&service_id=${subscriptionId}`, {
    headers: {
      'apikey': 'your_api_key'
    }
  });
  return await response.json();
};
```

#### Создание ссылки для оплаты
```javascript
const createPaymentLink = async (subscriptionId, feeId, userToken) => {
  const response = await fetch(`http://212.19.27.201/urban210/hs/api/v3/payment_link?service_id=${subscriptionId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'apikey': 'your_api_key',
      'usertoken': userToken
    },
    body: JSON.stringify({
      cart: [
        { purchase_id: feeId, count: 1 },
        { purchase_id: subscriptionId, count: 1 }
      ]
    })
  });
  return await response.json();
};
```

#### Управление подпиской
```javascript
// Получение подписок пользователя
const getUserSubscriptions = async (userToken) => {
  const response = await fetch('http://212.19.27.201/urban210/hs/api/v3/tickets?type=membership', {
    headers: {
      'apikey': 'your_api_key',
      'usertoken': userToken
    }
  });
  return await response.json();
};

// Заморозка подписки
const freezeSubscription = async (ticketId, days, userToken) => {
  const response = await fetch('http://212.19.27.201/urban210/hs/api/v3/freeze_ticket', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'apikey': 'your_api_key',
      'usertoken': userToken
    },
    body: JSON.stringify({
      ticket_id: ticketId,
      date: new Date().toISOString().split('T')[0],
      count: days
    })
  });
  return await response.json();
};
```

### React Hook пример
```javascript
import { useState, useEffect } from 'react';

const useSubscriptions = (userToken) => {
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSubscriptions = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://212.19.27.201/urban210/hs/api/v3/price_list?type=membership&club_id=b5f85d29-6727-11e9-80cb-00155d066506', {
          headers: {
            'apikey': process.env.REACT_APP_API_KEY
          }
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setSubscriptions(data.data || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSubscriptions();
  }, []);

  return { subscriptions, loading, error };
};
```

## 🔧 Переменные окружения

Для работы с API требуются следующие переменные:

```env
# API ключ для аутентификации
API_KEY=your_api_key_here

# Базовые учетные данные для HTTP аутентификации
API_USERNAME=your_username
API_PASSWORD=your_password

# Базовый URL API (опционально, для конфигурации)
API_BASE_URL=http://212.19.27.201/urban210/hs/api/v3
```

## 📋 Чек-лист для интеграции

- [ ] Настроены переменные окружения
- [ ] Реализована обработка ошибок HTTP статусов
- [ ] Добавлена валидация данных на фронтенде
- [ ] Реализовано сохранение user_token в localStorage/sessionStorage
- [ ] Добавлена обработка истечения токена
- [ ] Реализованы loading состояния для всех запросов
- [ ] Добавлена обработка сетевых ошибок
- [ ] Протестированы все основные сценарии

## 🚀 Готовые компоненты

Для быстрого старта можно использовать готовые компоненты:

```javascript
// Компонент выбора подписки
const SubscriptionSelector = ({ onSelect }) => {
  const { subscriptions, loading, error } = useSubscriptions();
  
  if (loading) return <div>Загрузка подписок...</div>;
  if (error) return <div>Ошибка: {error}</div>;
  
  return (
    <div>
      {subscriptions.map(sub => (
        <div key={sub.id} onClick={() => onSelect(sub)}>
          <h3>{sub.title}</h3>
          <p>{sub.price}</p>
          <p>{sub.available_time}</p>
        </div>
      ))}
    </div>
  );
};
``` 