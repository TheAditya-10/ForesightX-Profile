from __future__ import annotations

import asyncio

import httpx

from app.services.market_client import MarketDataClient


def test_get_prices_falls_back_to_zero_on_failure() -> None:
    async def _run() -> None:
        client = httpx.AsyncClient()
        try:
            market = MarketDataClient(base_url="http://data", http_client=client, service_name="test", max_retries=0)

            async def _fake_get_price(ticker: str) -> float:
                if ticker == "FAIL":
                    raise RuntimeError("boom")
                return 123.0

            market.get_price = _fake_get_price  # type: ignore[assignment]
            prices = await market.get_prices(["OK", "FAIL"])
            assert prices["OK"] == 123.0
            assert prices["FAIL"] == 0.0
        finally:
            await client.aclose()

    asyncio.run(_run())
