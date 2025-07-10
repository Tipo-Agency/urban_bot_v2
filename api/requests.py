from dotenv import load_dotenv
import os
from aiohttp import BasicAuth, ClientSession, ClientTimeout

load_dotenv()


class FitnessRequest:
    BASE_URL = "http://212.19.27.201/urban210/hs/api/v3"
    API_KEY = os.getenv("1C_API_KEY", "")  # Добавляем значение по умолчанию
    USERNAME = os.getenv("1C_USERNAME", "Adminbot")  # Добавляем значение по умолчанию
    PASSWORD = os.getenv("1C_PASSWORD", "RekBOT*012G")  # Добавляем значение по умолчанию
    
    # Проверяем, что значения не None перед созданием BasicAuth
    if USERNAME and PASSWORD:
        auth = BasicAuth(USERNAME, PASSWORD)
    else:
        # Если переменные окружения не установлены, используем значения по умолчанию
        auth = BasicAuth("Adminbot", "RekBOT*012G")
    
    # Настройка таймаута
    timeout = ClientTimeout(total=30)

    def __init__(self, user_token: str = None):
        self.user_token = user_token

    async def get_client(self):
        url = f"{self.BASE_URL}/client"
        headers = {
            "apikey": self.API_KEY or "",
            "usertoken": self.user_token or ""
        }
        try:
            async with ClientSession(auth=self.auth, timeout=self.timeout) as session:
                async with session.get(url, headers=headers) as response:
                    print("Status:", response.status)
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Error: {response.status}")
                        return None
        except Exception as e:
            print(f"Connection error: {e}")
            return None
            
    async def confirm_phone(self, phone: int, code: str):
        url = f"{self.BASE_URL}/confirm_phone"
        if not code:
            headers = {
                "apikey": self.API_KEY or "",
                "usertoken": self.user_token or "",
                "Content-Type": "application/json"
            }
            data = {
                "phone": phone,
                "auth_type": "whats_app"
            }
            try:
                async with ClientSession(auth=self.auth, timeout=self.timeout) as session:
                    async with session.post(url, headers=headers, json=data) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            print(f"Error: {response.status}")
                            return None
            except Exception as e:
                print(f"Connection error: {e}")
                return None
        if code:
            headers = {
                "apikey": self.API_KEY or "",
                "usertoken": self.user_token or "",
                "Content-Type": "application/json"
            }
            data = {
                "phone": phone,
                "code": code,
                "auth_type": "whats_app"
            }
            try:
                async with ClientSession(auth=self.auth, timeout=self.timeout) as session:
                    async with session.post(url, headers=headers, json=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            pass_token = result.get("data", {}).get("pass_token", "")
                            if pass_token:
                                return {"password_token": pass_token}
                            else:
                                return None
                        else:
                            print(f"Error: {response.status}")
                            return None
            except Exception as e:
                print(f"Connection error: {e}")
                return None
        return False
    
    async def set_password(self, pass_token: str, password: str, phone: int, last_name: str, name: str, second_name: str):
        url = f"{self.BASE_URL}/password"
        headers = {
            "Content-Type": "application/json",
            "apikey": self.API_KEY or "",
        }
        data = {
        "pass_token": pass_token,
        "password": password,
        "phone": phone,
        "last_name": last_name,
        "name": name,
        "second_name": second_name
        }
        import json
        try:
            async with ClientSession(auth=self.auth, timeout=self.timeout) as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Error: {response.status}")
                        return None
        except Exception as e:
            print(f"Connection error: {e}")
            return None
