import sys
sys.path.append('../')

import dotenv
import os
import pytest
import importlib
from aiopyqiwi.types.wallet import Wallet

dotenv.load_dotenv(dotenv.find_dotenv())
TOKEN = os.getenv("TOKEN")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

if not TOKEN or not PHONE_NUMBER:
    raise ValueError("TOKEN or PHONE_NUMBER not found in .env file")


class TestWallet:
    def setup_method(self):
        self.wallet = Wallet(token=TOKEN, phone=PHONE_NUMBER)
    
    def test_init(self):
        assert isinstance(self.wallet, Wallet)
        assert self.wallet.token == TOKEN
        assert self.wallet.phone == PHONE_NUMBER

    async def test_profile(self):
        profile = await self.wallet.profile
        assert isinstance(profile, dict)
        assert str(profile["authInfo"]["personId"]) == PHONE_NUMBER

    async def test_balance(self):
        balance = await self.wallet.balance
        assert isinstance(balance, float)

    async def test_get_history(self):
        history = await self.wallet.get_history()
        assert isinstance(history, list)
        assert len(history) == 10

        history_rows = await self.wallet.get_history(rows=20)
        assert len(history_rows) == 20

        history_all = await self.wallet.get_history(operation="ALL")
        assert len(history_all) == 10

    async def test_get_history_error(self):
        with pytest.raises(ValueError):
            await self.wallet.get_history(operation="ERROR")

    async def test_get_history_error_rows(self):
        with pytest.raises(ValueError):
            await self.wallet.get_history(rows=100)



