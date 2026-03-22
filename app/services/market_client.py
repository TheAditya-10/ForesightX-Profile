import asyncio

import httpx

from shared import get_logger, request_json


class MarketDataClient:
    def __init__(
        self,
        base_url: str,
        http_client: httpx.AsyncClient,
        service_name: str,
        max_retries: int,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.http_client = http_client
        self.max_retries = max_retries
        self.logger = get_logger(service_name, "market-client")

    async def get_price(self, ticker: str) -> float:
        payload = await request_json(
            client=self.http_client,
            method="GET",
            url=f"{self.base_url}/price/{ticker}",
            retries=self.max_retries,
            logger=self.logger,
        )
        return float(payload["price"])

    async def get_prices(self, tickers: list[str]) -> dict[str, float]:
        async def _fetch(ticker: str) -> tuple[str, float]:
            try:
                return ticker, await self.get_price(ticker)
            except Exception:
                self.logger.warning(f"Falling back to zero price for {ticker}")
                return ticker, 0.0

        results = await asyncio.gather(*[_fetch(ticker) for ticker in tickers])
        return dict(results)
