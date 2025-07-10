import sqlite3
import os
from typing import Optional, Dict, Any

DATABASE_PATH = 'users.db'

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY UNIQUE,
            user_id INTEGER UNIQUE,
            user_token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user_token_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Получить пользователя по ID"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_token, created_at FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return {
            'user_token': row[0],
            'created_at': row[1]
        }
    return None

def create_or_update_user(user_id: int, user_token: str):
    """Создать или обновить пользователя"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO users (id, user_id, user_token)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET 
        user_token=excluded.user_token
    ''', (str(user_id), user_id, user_token))
    
    conn.commit()
    conn.close()

def delete_user(user_id: int):
    """Удалить пользователя из базы данных"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    
    conn.commit()
    conn.close()

# Инициализируем базу данных при импорте модуля
init_db() 