import logging
import os

from aiohttp import BasicAuth, ClientSession, ClientTimeout
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

logger = logging.getLogger(__name__)


class FitnessAuthRequest:
    BASE_URL = "http://212.19.27.201/urban210/hs/api/v3"
    API_KEY = os.getenv("1C_API_KEY")
    USERNAME = os.getenv("1C_USERNAME")
    PASSWORD = os.getenv("1C_PASSWORD")
    PROXY_URL = os.getenv("PROXY_URL")

    auth = BasicAuth(str(USERNAME), str(PASSWORD))

    timeout = ClientTimeout(total=30)

    def __init__(self, user_token: str = ""):
        self.user_token = user_token

    async def get_client(self):
        url = f"{self.BASE_URL}/client"
        headers = {"apikey": self.API_KEY or "", "usertoken": self.user_token or ""}
        try:
            async with ClientSession(auth=self.auth, timeout=self.timeout) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        logger.debug(f"✅ Успешный запрос get_client")
                        return await response.json()
                    else:
                        logger.error(f"❌ Ошибка get_client: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"❌ Ошибка соединения get_client: {e}")
            return None

    async def auth_client(self, phone: int, password: str):
        url = f"{self.BASE_URL}/auth_client"
        headers = {
            "Content-Type": "application/json",
            "apikey": self.API_KEY or "",
        }
        data = {"phone": phone, "password": password}

        try:
            async with ClientSession(auth=self.auth, timeout=self.timeout) as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        logger.debug(f"✅ Успешная авторизация клиента")
                        return await response.json()
                    else:
                        logger.error(f"❌ Ошибка auth_client: {response.status}")
                        logger.error(f"❌ Ответ сервера: {await response.text()}")
                        return None
        except Exception as e:
            logger.error(f"❌ Ошибка соединения auth_client: {e}")
            return None

    async def auth_and_register(
        self,
        phone: int,
        password: str,
        last_name: str,
        name: str,
        second_name: str,
        email: str,
        birth_date: str,
        pass_token: str = "",
        autopassword_to_sms: bool = False,
    ):
        url = f"{self.BASE_URL}/reg_and_auth_client"
        headers = {
            "Content-Type": "application/json",
            "apikey": self.API_KEY or "",
        }
        data = {
            "phone": phone,
            "password": password,
            "pass_token": pass_token,
            "last_name": last_name,
            "name": name,
            "second_name": second_name,
            "email": email,
            "birth_date": birth_date,
            "autopassword_to_sms": autopassword_to_sms,
        }
        try:
            async with ClientSession(auth=self.auth, timeout=self.timeout) as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        logger.debug(f"✅ Успешная регистрация и авторизация")
                        return await response.json()
                    else:
                        logger.error(f"❌ Ошибка auth_and_register: {response.status}")
                        logger.error(f"❌ Ответ сервера: {await response.text()}")
                        return None
        except Exception as e:
            logger.error(f"❌ Ошибка соединения auth_and_register: {e}")
            return None

    async def confirm_phone(self, phone: int, code: str):
        url = f"{self.BASE_URL}/confirm_phone"
        if not code:
            headers = {
                "apikey": self.API_KEY or "",
                "usertoken": self.user_token or "",
                "Content-Type": "application/json",
            }
            data = {"phone": phone, "auth_type": "whats_app"}
            try:
                async with ClientSession(
                    auth=self.auth, timeout=self.timeout
                ) as session:
                    async with session.post(
                        url, headers=headers, json=data
                    ) as response:
                        if response.status == 200:
                            logger.debug(f"✅ Успешная отправка кода подтверждения")
                            return await response.json()
                        else:
                            logger.error(f"❌ Ошибка отправки кода: {response.status}")
                            return None
            except Exception as e:
                logger.error(f"❌ Ошибка соединения при отправке кода: {e}")
                return None
        if code:
            headers = {"apikey": self.API_KEY or "", "Content-Type": "application/json"}
            data = {"phone": phone, "confirmation_code": code, "auth_type": "whats_app"}
            try:
                async with ClientSession(
                    auth=self.auth, timeout=self.timeout
                ) as session:
                    async with session.post(
                        url, headers=headers, json=data
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            pass_token = result.get("data", {}).get("pass_token", "")
                            if pass_token:
                                return {"password_token": pass_token}
                            else:
                                return None
                        else:
                            logger.error(f"❌ Ошибка подтверждения кода: {response.status}")
                            return None
            except Exception as e:
                logger.error(f"❌ Ошибка соединения при подтверждении кода: {e}")
                return None
        return False

    async def set_password(
        self,
        pass_token: str,
        password: str,
        phone: int,
        last_name: str,
        name: str,
        second_name: str,
    ):
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
            "second_name": second_name,
        }
        try:
            async with ClientSession(auth=self.auth, timeout=self.timeout) as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        logger.debug(f"✅ Успешная установка пароля")
                        return await response.json()
                    else:
                        logger.error(f"❌ Ошибка set_password: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"❌ Ошибка соединения set_password: {e}")
            return None


class FitnessSubscriptionRequest(FitnessAuthRequest):
    async def get_subscriptions(self):
        url = f"{self.BASE_URL}/price_list?type=membership&club_id=b5f85d29-6727-11e9-80cb-00155d066506"
        headers = {
            "apikey": self.API_KEY,
        }
        try:
            async with ClientSession(auth=self.auth, timeout=self.timeout) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "subscriptions": [
                                {
                                    "id": item.get("id", ""),
                                    "title": item.get("title", ""),
                                    "price": item.get("price", ""),
                                    "available_time": item.get("available_time", ""),
                                    "fee": {
                                        "id": item.get("fee", {}).get("id", ""),
                                        "title": item.get("fee", {}).get("title", ""),
                                        "price": item.get("fee", {}).get("price", ""),
                                    },
                                }
                                for item in data.get("data", [])
                            ]
                        }
                    else:
                        print(f"Error: {response.status}")
                        return None
        except Exception as e:
            print(f"Connection error: {e}")
            return None

    async def get_subscription_details(self, subscription_id: str):
        url = f"{self.BASE_URL}/price_list?type=membership&club_id=b5f85d29-6727-11e9-80cb-00155d066506&service_id={subscription_id}"
        headers = {"apikey": self.API_KEY}
        try:
            async with ClientSession(auth=self.auth, timeout=self.timeout) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Получаем первый элемент из списка подписок (обычно он один)
                        subscription_data = (data.get("data") or [{}])[0]

                        # Извлекаем данные о вступительном взносе, если есть
                        fee_data = subscription_data.get("fee") or {}

                        # Формируем красивый и понятный словарь с деталями подписки
                        subscription = {
                            "id": subscription_data.get("id", ""),
                            "title": subscription_data.get("title", ""),
                            "description": subscription_data.get("description", ""),
                            "price": subscription_data.get("price", ""),
                            "available_time": subscription_data.get(
                                "available_time", ""
                            ),
                            "validity_period": (
                                subscription_data.get("validity") or {}
                            ).get("validity_description", ""),
                            "restriction": subscription_data.get("restriction", ""),
                            "fee": {
                                "id": fee_data.get("id", ""),
                                "title": fee_data.get("title", ""),
                                "price": fee_data.get("price", ""),
                            },
                        }

                        return {"subscription": subscription}
                    else:
                        logger.error(f"❌ Ошибка get_subscription_details: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"❌ Ошибка соединения get_subscription_details: {e}")
            return None

    async def get_payment_link(
        self,
        subscription_id: str,
        fee_id: str,
    ):
        url = f"{self.BASE_URL}/payment_link?service_id={subscription_id}"
        headers = {"apikey": self.API_KEY, "usertoken": self.user_token}
        data = {
            "cart": [
                {"purchase_id": fee_id, "count": 1},
                {"purchase_id": subscription_id, "count": 1},
            ],
            # "club_id": "b5f85d29-6727-11e9-80cb-00155d066506",
        }
        try:
            async with ClientSession(auth=self.auth) as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.debug(f"✅ Получена ссылка на оплату")
                        return result.get("data", {}).get("link", "")
                    else:
                        logger.error(f"❌ Ошибка get_payment_link: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"❌ Ошибка соединения get_payment_link: {e}")
            return None
        
    async def get_user_subscriptions(self):
        """Получает список подписок пользователя"""
        url = f"{self.BASE_URL}/tickets?type=membership"
        headers = {"apikey": self.API_KEY, "usertoken": self.user_token}
        try:
            async with ClientSession(auth=self.auth, timeout=self.timeout) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("result"):
                            return {
                                "subscriptions": [
                                    {
                                        "ticket_id": item.get("ticket_id", ""),
                                        "item_id": item.get("item_id", ""),
                                        "type": item.get("type", ""),
                                        "status": item.get("status", ""),
                                        "end_date": item.get("end_date", ""),
                                        "status_date": item.get("status_date", ""),
                                        "active_date": item.get("active_date", ""),
                                        "title": item.get("title", ""),
                                        "service_list": item.get("service_list", []),
                                        "recurrent": item.get("recurrent", False),
                                        "recurrent_details": item.get("recurrent_details", {}),
                                        "available_time": item.get("available_time", ""),
                                        "available_actions": item.get("avialable_actions", [])
                                    }
                                    for item in data.get("data", [])
                                ]
                            }
                    else:
                        logger.error(f"❌ Ошибка get_user_subscriptions: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"❌ Ошибка соединения get_user_subscriptions: {e}")
            return None
        
    async def cancel_subscription(self, recurrent_id: str):
        """Отменяет подписку пользователя"""
        url = f"{self.BASE_URL}/cancellation_contract?id={recurrent_id}&reason_id=d3bc2a44-9aa2-11ee-bbbe-8b03c544a7da"
        headers = {"apikey": self.API_KEY, "usertoken": self.user_token}
        try:
            async with ClientSession(auth=self.auth, timeout=self.timeout) as session:
                async with session.delete(url, headers=headers) as response:
                    if response.status == 200:
                        logger.debug(f"✅ Подписка {recurrent_id} успешно отменена")
                        logger.degug(f"✅ Данные Ответа: {await response.json()}")
                        return await response.json()
                    else:
                        logger.error(f"❌ Ошибка cancel_subscription: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"❌ Ошибка соединения cancel_subscription: {e}")
            return None
        
    async def check_payment(self, subscription_id: str):
        """Проверяет статус оплаты подписки"""
        subscriptions_data = await self.get_user_subscriptions()
        if subscriptions_data:
            for subscription in subscriptions_data.get("subscriptions", []):
                if subscription.get("item_id") == subscription_id:
                    if subscription.get("status") == "active" and subscription.get("active_date"):
                        #Проверяем, совпадает ли дата активации с сегодняшней датой
                        try:
                            active_date = subscription.get("active_date")
                            # Предполагаем формат даты "YYYY-MM-DD" или "YYYY-MM-DDTHH:MM:SS"
                            date_part = active_date.split("T")[0]
                            today = datetime.now().date().isoformat()
                            if date_part == today:
                                return True
                        except Exception as e:
                            logger.error(f"❌ Ошибка парсинга даты: {e}")
                            continue
        return False
