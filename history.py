import logging
from collections import defaultdict
import time

logger = logging.getLogger(__name__)

chat_history = defaultdict(list)
last_seen = defaultdict(lambda: time.time())
MAX_HISTORY_LENGTH = 6
HISTORY_TIMEOUT = 600  # 10 минут в секундах

def update_user_history(user_id: int, user_msg: str, bot_reply: str):
    now = time.time()
    last_seen[user_id] = now

    chat_history[user_id].append({"role": "user", "content": user_msg})
    chat_history[user_id].append({"role": "assistant", "content": bot_reply})
    if len(chat_history[user_id]) > MAX_HISTORY_LENGTH:
        chat_history[user_id] = chat_history[user_id][-MAX_HISTORY_LENGTH:]
    
    logger.debug(f"📝 Обновлена история для пользователя {user_id}")

def clear_user_history(user_id: int):
    chat_history.pop(user_id, None)
    last_seen.pop(user_id, None)
    logger.debug(f"🗑️ Очищена история для пользователя {user_id}")

