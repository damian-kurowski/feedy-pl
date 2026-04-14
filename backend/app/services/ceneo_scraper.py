"""Ceneo competitor price scraper.

Searches Ceneo by EAN and returns top offers. Designed to be replaceable
(if Ceneo changes their HTML, only this file needs updating) and to fail
gracefully — never raise, always return a structured result.

Caveats:
  - Ceneo HTML structure changes occasionally; selectors below are best-effort
  - Throttle requests to avoid being blocked (default: 1 req per 2s)
  - Respect robots.txt — only public search pages
"""
from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass, field

import httpx
from lxml import html as lxml_html


CENEO_BASE = "https://www.ceneo.pl"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

THROTTLE_SECONDS = 2.0
_last_request_at: float = 0.0


@dataclass
class CeneoOffer:
    seller: str
    price: float
    url: str | None = None


@dataclass
class CeneoResult:
    """Result of scraping Ceneo for one product."""
    found: bool = False
    offers: list[CeneoOffer] = field(default_factory=list)
    lowest_price: float | None = None
    lowest_seller: str | None = None
    total_offers: int = 0
    error: str | None = None


def _parse_price(raw: str) -> float | None:
    if not raw:
        return None
    cleaned = re.sub(r"[^\d,.]", "", raw).replace(",", ".")
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


async def _throttled_get(client: httpx.AsyncClient, url: str) -> httpx.Response | None:
    """GET with global per-process throttling. Returns None on error."""
    global _last_request_at
    now = time.monotonic()
    elapsed = now - _last_request_at
    if elapsed < THROTTLE_SECONDS:
        await asyncio.sleep(THROTTLE_SECONDS - elapsed)
    _last_request_at = time.monotonic()
    try:
        resp = await client.get(url, headers=DEFAULT_HEADERS, follow_redirects=True, timeout=10.0)
        if resp.status_code != 200:
            return None
        return resp
    except (httpx.RequestError, httpx.HTTPStatusError):
        return None


def _parse_offers_from_html(html: str) -> list[CeneoOffer]:
    """Best-effort parse of Ceneo product page offers.

    Ceneo product pages have multiple offer cards. We try several selectors
    because the markup occasionally shifts.
    """
    if not html:
        return []
    try:
        tree = lxml_html.fromstring(html)
    except Exception:
        return []

    offers: list[CeneoOffer] = []

    # Strategy 1: product offer rows on a comparison page (/{id}.html)
    for offer_el in tree.xpath('//div[contains(@class, "product-offer")]'):
        seller_el = offer_el.xpath('.//a[contains(@class, "go-to-shop")] | .//span[contains(@class, "shop-name")]')
        price_el = offer_el.xpath('.//span[contains(@class, "price-format__price")] | .//span[contains(@class, "value")]')
        if not price_el:
            continue
        price_text = "".join(price_el[0].itertext()).strip() if hasattr(price_el[0], "itertext") else str(price_el[0])
        price = _parse_price(price_text)
        if price is None:
            continue
        seller_text = ""
        if seller_el:
            seller_text = "".join(seller_el[0].itertext()).strip() if hasattr(seller_el[0], "itertext") else str(seller_el[0])
        offers.append(CeneoOffer(seller=seller_text or "(unknown)", price=price))

    # Strategy 2: search result tiles (no exact product match)
    if not offers:
        for tile in tree.xpath('//div[contains(@class, "cat-prod-row")]'):
            price_el = tile.xpath('.//span[contains(@class, "price")]')
            if not price_el:
                continue
            price_text = "".join(price_el[0].itertext()).strip()
            price = _parse_price(price_text)
            if price is None:
                continue
            offers.append(CeneoOffer(seller="(z wyszukiwarki)", price=price))

    # Sort ascending by price
    offers.sort(key=lambda o: o.price)
    return offers


async def search_by_ean(ean: str, *, limit: int = 10) -> CeneoResult:
    """Search Ceneo by EAN, return parsed offers.

    Returns a CeneoResult with found=False and an error string if anything fails.
    """
    if not ean or not ean.strip().isdigit():
        return CeneoResult(error="Brak EAN")

    search_url = f"{CENEO_BASE}/;szukaj-{ean.strip()}"
    async with httpx.AsyncClient() as client:
        resp = await _throttled_get(client, search_url)
        if resp is None:
            return CeneoResult(error="Ceneo niedostępne lub blokuje boty")

        offers = _parse_offers_from_html(resp.text)
        if not offers:
            return CeneoResult(found=False, error="Brak wyników w Ceneo")

        offers = offers[:limit]
        lowest = offers[0]
        return CeneoResult(
            found=True,
            offers=offers,
            lowest_price=lowest.price,
            lowest_seller=lowest.seller,
            total_offers=len(offers),
        )
