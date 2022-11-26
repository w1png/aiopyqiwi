import aiohttp
import re


class Wallet:
    """
    Класс для работы с кошельком.
    """
    def __init__(self, token: str, phone: str) -> None:
        self.token = token

        if not re.match(r"^(7|8|\+7)\d{10}$", phone):
            raise ValueError("phone must in +7XXXXXXXXXX format")
        self.phone = phone

        self.HEADERS = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    @property
    async def profile(self) -> dict:
        """
        Получение информации о профиле.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get("https://edge.qiwi.com/person-profile/v1/profile/current", headers=self.HEADERS) as response:
                return await response.json()

    @property
    async def balance(self) -> float:
        """
        Получение баланса кошелька в рублях.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://edge.qiwi.com/funding-sources/v2/persons/{self.phone}/accounts", headers=self.HEADERS) as response:
                return (await response.json())["accounts"][0]["balance"]["amount"]

    async def get_history(self, rows: int=10, operation: str="IN") -> list:
        """
        Получение истории операций.
        """
        if operation not in ["IN", "OUT", "ALL", "QIWI_CARD"]:
            raise ValueError("operation must be IN, OUT, ALL or QIWI_CARD")
        if rows > 50:
            raise ValueError("rows must be less than 50")

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"https://edge.qiwi.com/payment-history/v2/persons/{self.phone}/payments",
                    params={"rows": rows, "operation": operation},
                    headers=self.HEADERS,
            ) as response:
                return (await response.json())["data"]

    async def transfer(self, amount: float, comment: str, to: str) -> dict:
        """
        Перевод денег на другой кошелек.
        """
        if not re.match(r"^(7|8|\+7)\d{10}$", to):
            raise ValueError("to must be in +7XXXXXXXXXX format")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"https://edge.qiwi.com/sinap/api/v2/terms/99/payments",
                    json={
                        "id": "string",
                        "sum": {
                            "amount": amount,
                            "currency": "643"
                        },
                        "paymentMethod": {
                            "type": "Account",
                            "accountId": "643"
                        },
                        "fields": {
                            "account": to
                        },
                        "comment": comment
                    },
                    headers=self.HEADERS,
            ) as response:
                return await response.json()

