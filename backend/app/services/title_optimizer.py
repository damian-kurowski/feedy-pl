"""Smart title optimization for product feeds.

Uses pattern-based optimization for MVP. Can be upgraded to LLM-based later.
"""
import re


def optimize_title(
    title: str,
    brand: str | None = None,
    category: str | None = None,
    color: str | None = None,
    size: str | None = None,
    max_length: int = 150,
) -> str:
    """Optimize a product title for better visibility on comparison sites.

    Strategy:
    1. Clean up: remove excessive whitespace, HTML, special chars
    2. Ensure brand is at the beginning
    3. Add key attributes (color, size) if not already present
    4. Truncate to max_length
    """
    if not title:
        return ""

    # Clean
    result = re.sub(r"<[^>]+>", "", title)  # strip HTML
    result = re.sub(r"\s+", " ", result).strip()  # normalize whitespace
    result = re.sub(r"[^\w\s.,\-/()łąęśżźćńóŁĄĘŚŻŹĆŃÓ]", "", result)  # keep Polish chars

    # Ensure brand at beginning
    if brand and brand.strip():
        brand_clean = brand.strip()
        if not result.lower().startswith(brand_clean.lower()):
            result = f"{brand_clean} {result}"

    # Add attributes if not present
    extras = []
    if color and color.strip() and color.lower() not in result.lower():
        extras.append(color.strip())
    if size and size.strip() and size.lower() not in result.lower():
        extras.append(size.strip())

    if extras:
        suffix = " - " + ", ".join(extras)
        if len(result) + len(suffix) <= max_length:
            result += suffix

    # Truncate
    if len(result) > max_length:
        result = result[:max_length - 3].rsplit(" ", 1)[0] + "..."

    return result


def optimize_titles_bulk(products: list[dict]) -> list[dict]:
    """Optimize titles for all products in a list.

    Each product has 'product_value' dict.
    Returns new list with optimized titles (doesn't mutate originals).
    """
    from app.services.feed_generator import _get_value

    result = []
    for product in products:
        pv = product["product_value"].copy()

        title = _get_value(pv, "title") or ""
        brand = _get_value(pv, "g:brand")
        category = _get_value(pv, "g:product_type")
        color = _get_value(pv, "g:color") or pv.get("color")
        size = _get_value(pv, "g:size") or pv.get("size")

        optimized = optimize_title(title, brand=brand, category=category, color=color, size=size)

        # Update the title field (try multiple names)
        for key in ["title", "name"]:
            if key in pv:
                pv[key] = optimized
                break
        else:
            pv["title"] = optimized

        result.append({"product_value": pv})

    return result
