import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class AbstractVolatilityManager(ABC):
    def __init__(self, url: str, timeout: int = 10, retries: int = 3) -> None:
        self.url = url
        self.client = httpx.AsyncClient(timeout=timeout)
        self.retries = retries

    @abstractmethod
    async def fetch_data(
        self,
        symbol: str,
        interval: str,
        **kwargs: Any,
    ) -> list[list[int | str]]:
        """
        Abstract method to fetch data for a given symbol and interval.
        Must be implemented by subclasses. Note that this method must use
        the self.client attribute and it must transform the data into the
        structure expected by calculate_volatility.
        """

    async def get_response(
        self,
        symbol: str,
        interval: str,
        **kwargs: Any,
    ) -> list[list[int | str]] | None:
        for attempt in range(self.retries):
            try:
                data = await self.fetch_data(symbol, interval, **kwargs)
                if data:
                    return data
            except httpx.RequestError:
                logging.exception(
                    f"RequestError for {symbol} on attempt {attempt + 1}",
                )
            except httpx.HTTPStatusError:
                logging.exception(
                    f"HTTPStatusError for {symbol} on attempt {attempt + 1}",
                )
            except asyncio.TimeoutError:
                logging.exception(f"TimeoutError for {symbol} on attempt {attempt + 1}")
            except Exception:
                logging.exception(
                    f"Unexpected error for {symbol} on attempt {attempt + 1}",
                )

            await asyncio.sleep(1)

    async def get_responses(
        self,
        symbols: list[str],
        interval: str,
        **kwargs: Any,
    ) -> list[list[list[int | str]] | None]:
        tasks = [self.get_response(symbol, interval, **kwargs) for symbol in symbols]
        return await asyncio.gather(*tasks)

    async def calculate_volatility(
        self,
        symbols: list[str],
        interval: str,
        **kwargs: Any,
    ) -> dict[str, float]:
        result = await self.get_responses(symbols, interval, **kwargs)
        volatility_map = {}
        max_value = -float("inf")
        min_value = float("inf")

        for symbol, data in zip(symbols, result):
            if data:
                for array in data:
                    high_price = float(array[2])
                    low_price = float(array[3])

                    if high_price > max_value:
                        max_value = high_price

                    if low_price < min_value:
                        min_value = low_price

                if min_value > 0:
                    volatility = (max_value - min_value) / min_value * 100
                    volatility_map[symbol] = volatility
                else:
                    logging.warning(
                        f"Min value is zero for {symbol}, skipping volatility calculation.",
                    )
            else:
                logging.warning(f"No data received for {symbol}.")

        logging.info(f"Volatility map: {volatility_map}")
        return volatility_map
