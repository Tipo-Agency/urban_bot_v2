import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-mini"


# Пример базы знаний сервиса
BASE_KNOWLEDGE = """
  Вот краткая информация о нашем сервисе:
- Пользователи могут купить онлайн-подписку на тренировки
- Доступ предоставляется через личный кабинет
- Видеотренировки, планы питания, расписание и чат с тренерами (если включено)
- Подписку можно приостановить в любой момент
- Доступ к курсам предоставляется на время действия подписки
- После прохождения курса может выдаваться сертификат (если предусмотрено)

  Условия оплаты:
- Вступительный взнос: 3000 ₽ (разово, при первой покупке)
- Далее — ежемесячное списание в зависимости от выбранного тарифа

   Тарифы (подписки):
1. SmartFit — 1300 ₽/мес  
   Доступ: 07:00–17:30 и 20:30–23:30

2. FitFlow — 1700 ₽/мес  
   Безлимитный доступ в любое время

3. ProFit — 2400 ₽/мес  
   Безлимит + групповые программы

  Важно:
- Не выдумывай лишнего, если нет инфы — честно скажи: «Пожалуйста, уточните у оператора»
- Общайся по-человечески, дружелюбно, с пониманием
"""

# Проверка валидного имени
def is_valid_name(name: str) -> bool:
    return name and name.isalpha() and len(name) > 1

async def get_llm_response(user_message: str, telegram_name: str = "", history: list = None) -> str:
    user_name = telegram_name if is_valid_name(telegram_name) else ""
    history = history or []

    system_prompt = f"""
    Ты — специалист поддержки сервиса Urban210.
    📌 О сервисе:
    {BASE_KNOWLEDGE}

    ❗Ты не бот и не ИИ. Отвечай как сотрудник, по-человечески и понятно. Имя пользователя: {user_name}
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://urban210.jam",
        "X-Title": "Urban210SupportBot"
    }

    messages = [{"role": "system", "content": system_prompt}] + history + [
        {"role": "user", "content": user_message}
    ]

    data = {
        "model": MODEL,
        "messages": messages
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(OPENROUTER_API_URL, json=data, headers=headers) as resp:
            res = await resp.json()
            return res["choices"][0]["message"]["content"]


