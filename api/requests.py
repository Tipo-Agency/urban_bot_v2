from dotenv import load_dotenv
import os
from aiohttp import BasicAuth, ClientSession

load_dotenv()


class FitnessRequest:
    BASE_URL = "http://212.19.27.201/urban210/hs/api/v3"
    API_KEY = os.getenv("1C_API_KEY")  # или просто подставь строку
    USERNAME = os.getenv("1C_USERNAME")  # "Adminbot"
    PASSWORD = os.getenv("1C_PASSWORD")  # "RekBOT*012G"
    auth = BasicAuth(USERNAME, PASSWORD)

    def __init__(self, user_token: str = None):
        self.user_token = user_token

    async def get_client(self):
        url = f"{self.BASE_URL}/client"
        headers = {
            "apikey": self.API_KEY,
            "usertoken": self.user_token
        }
        async with ClientSession(auth=self.auth) as session:
            async with session.get(url, headers=headers) as response:
                print("Status:", response.status)
                if response.status == 200:
                    return await response.json()
                else:
                    return None
            
    async def confirm_phone(self, phone: int, code: str):
        url = f"{self.BASE_URL}/confirm_phone"
        if not code:
            headers = {
                "apikey": self.API_KEY,
                "usertoken": self.user_token,
                "phone": phone,
                "auth_type": "whats_app"
            }
            async with ClientSession(auth=self.auth) as session:
                async with session.post(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return None
        if code:
            headers = {
                "apikey": self.API_KEY,
                "usertoken": self.user_token,
                "phone": phone,
                "code": code,
                "auth_type": "whats_app"
            }
            async with ClientSession(auth=self.auth) as session:
                async with session.post(url, headers=headers) as response:
                    if response.status == 200:
                        pass_token = await response.json().get("pass_token")
                        if pass_token:
                            return {"password_token": pass_token}
                        else:
                            return None
                    else:
                        return None
        return False
    
    async def set_password(self, pass_token: str, password: str, phone: int, last_name: str, name: str, second_name: str):
        url = f"{self.BASE_URL}/password"
        headers = {
            "Content-Type": "application/json",
            "apikey": self.API_KEY,
        }
        data = {
        "pass_token": pass_token,
        "password": password,
        "phone": phone,
        "last_name": last_name,
        "name": name,
        "second_name": second_name
        }
        async with ClientSession(auth=self.auth) as session:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
