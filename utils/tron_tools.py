import asyncio
import time
from decimal import Decimal,ROUND_DOWN

import aiohttp
from tronpy import AsyncTron
from tronpy.keys import PrivateKey


class TronTools:
    _price_cache = {"timestamp": 0, "data": None}
    _cache_expiry = 5  # Second

    @staticmethod
    async def get_balance(wallet_address: str) -> float:
        """
        :param wallet_address:
        :return: Trx Balance
        """
        async with AsyncTron() as client:
            balance = await client.get_account_balance(wallet_address)
            return balance

    @staticmethod
    async def get_trx_to_toman() -> dict:
        now = time.time()
        if TronTools._price_cache["data"] and now - TronTools._price_cache["timestamp"] < TronTools._cache_expiry:
            return TronTools._price_cache["data"]

        API_URL = "https://apiv2.nobitex.ir/v3/orderbook/TRXIRT"
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as response:
                data = await response.json()

                if data.get("status") != "ok":
                    raise Exception("خطا در دریافت اطلاعات از نوبیتکس")

                best_bid = Decimal(data["bids"][0][0])
                best_ask = Decimal(data["asks"][0][0])
                avg_price = (best_bid + best_ask) / 2

                result = {
                    "best_buy": (best_bid / 10).quantize(Decimal("0.01"), rounding=ROUND_DOWN),
                    "best_sell": (best_ask / 10).quantize(Decimal("0.01"), rounding=ROUND_DOWN),
                    "average": (avg_price / 10).quantize(Decimal("0.01"), rounding=ROUND_DOWN),
                }

                TronTools._price_cache["data"] = result
                TronTools._price_cache["timestamp"] = now
                return result

    @staticmethod
    async def convert_trx_to_toman(trx: float) -> int:
        data = await TronTools.get_trx_to_toman()
        trx_dec = Decimal(str(trx))
        return (trx_dec * data["average"]).quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    @staticmethod
    async def convert_toman_to_trx(toman: int) -> float:
        data = await TronTools.get_trx_to_toman()
        toman_dec = Decimal(str(toman))
        return (toman_dec / data["average"]).quantize(Decimal("0.000001"), rounding=ROUND_DOWN)

    @staticmethod
    async def send_trx(from_priv_key: str, to_address: str, amount: float) -> dict:
        """
        پارامترها:
            from_priv_key (str): کلید خصوصی ولت فرستنده
            to_address (str): آدرس ولت گیرنده
            amount (float): مقدار TRX برای ارسال
        خروجی:
            dict: نتیجه تراکنش شامل txid و وضعیت
        """
        priv_key = PrivateKey(bytes.fromhex(from_priv_key))
        from_address = priv_key.public_key.to_base58check_address()

        async with AsyncTron(network="nile") as client: # TODO Go Default Network
            balance = await client.get_account_balance(from_address)
            if balance < amount:
                raise Exception("موجودی کافی نیست")

            txb = (
                client.trx.transfer(
                    priv_key.public_key.to_base58check_address(),
                    to_address,
                    int(amount * 1_000_000)
                )
                .memo("Transfer via tronpy async")
                .fee_limit(5_000_000)
            )

            txn = await txb.build()
            signed_txn = txn.sign(priv_key)
            result = await signed_txn.broadcast()
            receipt = await result.wait()

            return {
                "txid": result["txid"],
                "status": receipt
            }

    @staticmethod
    def get_tronscan_url(txid: str) -> str:
        return rf"https://tronscan.org/#/transaction/{txid}"

    @staticmethod
    def create_trx_wallet():
        private_key = PrivateKey.random()
        address = private_key.public_key.to_base58check_address()

        return {
            "private_key": private_key.hex(),
            "address": address
        }

