"""AI-powered description rewriting using Claude API."""

import os
from typing import Optional


_PLATFORM_PROMPTS = {
    "gmc": "Przepisz opis produktu dla Google Shopping. Max {max_length} znakow. Bez HTML, bez tekstu promocyjnego typu 'kup teraz', 'najlepszy'. Kluczowe cechy produktu na poczatku. Zachowaj fakty i specyfikacje.",
    "facebook": "Przepisz opis produktu dla reklam Facebook/Instagram. Pierwsze 125 znakow sa najwazniejsze. Podkresl korzysci dla kupujacego. Max {max_length} znakow.",
    "ceneo": "Przepisz opis produktu dla poronywarki cen Ceneo. 200-1000 znakow. Techniczny, ze specyfikacjami i kluczowymi parametrami. Bez marketingowego jezyka.",
    "skapiec": "Przepisz opis produktu dla poronywarki cen. 200-1000 znakow. Techniczny, ze specyfikacjami i kluczowymi parametrami.",
    "allegro": "Przepisz opis produktu dla Allegro. Szczegolowy opis z parametrami technicznymi. Max {max_length} znakow.",
    "domodi": "Przepisz opis produktu modowego. Podkresl styl, material, okazje do noszenia. Max {max_length} znakow.",
}

_DEFAULT_MAX_LENGTH = {
    "gmc": 5000,
    "facebook": 9999,
    "ceneo": 1000,
    "skapiec": 1000,
    "allegro": 2000,
    "domodi": 1000,
}


def get_api_key() -> Optional[str]:
    return os.environ.get("ANTHROPIC_API_KEY")


def is_ai_available() -> bool:
    return get_api_key() is not None


async def rewrite_description(
    product_name: str,
    original_desc: str,
    platform: str,
    max_length: int | None = None,
) -> str:
    """Rewrite a product description using Claude API.

    Returns the rewritten description, or the original if AI is unavailable.
    """
    api_key = get_api_key()
    if not api_key:
        return original_desc

    if not max_length:
        max_length = _DEFAULT_MAX_LENGTH.get(platform, 5000)

    system_prompt = _PLATFORM_PROMPTS.get(platform, _PLATFORM_PROMPTS["gmc"]).format(max_length=max_length)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Nazwa produktu: {product_name}\n\nOryginalny opis:\n{original_desc[:3000]}",
                }
            ],
        )
        return message.content[0].text.strip()
    except Exception:
        return original_desc


async def rewrite_descriptions_bulk(
    products: list[dict],
    platform: str,
    limit: int = 10,
) -> list[dict]:
    """Rewrite descriptions for multiple products.

    Each product dict must have ``product_name`` and ``product_value`` keys.
    Returns list of {product_name, product_id, original, rewritten}.
    """
    results = []
    desc_keys = ["description", "desc", "g:description"]

    for product in products[:limit]:
        pv = product.get("product_value", {})
        pid = product.get("id", 0)
        name = product.get("product_name", "")

        # Find description field
        original = ""
        for key in desc_keys:
            if key in pv and pv[key]:
                original = str(pv[key])
                break

        if not original:
            continue

        rewritten = await rewrite_description(name, original, platform)
        results.append({
            "product_id": pid,
            "product_name": name,
            "original": original[:500],
            "rewritten": rewritten[:500] if rewritten != original else original[:500],
            "changed": rewritten != original,
        })

    return results
