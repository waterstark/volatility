import asyncio
import logging
from typing import Any

import httpx
from volatility_manager import AbstractVolatilityManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class BinanceVolatilityManager(AbstractVolatilityManager):
    async def fetch_data(
        self,
        symbol: str,
        interval: str,
        **kwargs: Any,
    ) -> list[list[dict[str, Any]] | None] | None:
        params = {"symbol": symbol, "interval": interval}
        params.update(kwargs)
        response = await self.client.get(self.url, params=params)

        if response.status_code == httpx.codes.OK:
            data = response.json()
            if isinstance(data, list):
                return data
            logging.error(f"Unexpected JSON format for {symbol}")
        else:
            logging.error(f"{symbol} - Status: {response.status_code}")


async def main():
    url = "https://api.binance.com/api/v3/klines"
    manager = BinanceVolatilityManager(url)
    res = await manager.calculate_volatility(
        symbols=["BTCUSDT", "ETHBTC", "LTCBTC", "ABOBABTC", "DGBBTC", "DOGEBTC"],
        interval="1m",
        limit=60,
    )
    logging.info(res)


if __name__ == "__main__":
    asyncio.run(main())
