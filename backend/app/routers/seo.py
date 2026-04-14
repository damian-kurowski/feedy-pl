"""SEO endpoints: dynamic sitemap.xml and HTML rendering for blog/landing pages."""
import json
import os
import re
import time
from datetime import date, datetime
from html import escape

import httpx
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.blog_post import BlogPost
from app.models.landing_page import LandingPage

router = APIRouter(tags=["seo"])

SITE = "https://feedy.pl"

# Static SEO routes — kept in sync with frontend/scripts/seo-routes.mjs
STATIC_ROUTES = [
    ("/", "1.0", "weekly"),
    ("/blog", "0.8", "weekly"),
    ("/feed-ceneo", "0.9", "monthly"),
    ("/feed-google-shopping", "0.9", "monthly"),
    ("/feed-allegro", "0.8", "monthly"),
    ("/integracja-shoper", "0.8", "monthly"),
    ("/integracja-woocommerce", "0.8", "monthly"),
    ("/porownanie/feedy-vs-datafeedwatch", "0.7", "monthly"),
    ("/oferty/cennik", "0.6", "monthly"),
    ("/blog/jak-dodac-produkty-do-ceneo", "0.7", "monthly"),
    ("/blog/jak-stworzyc-feed-xml", "0.7", "monthly"),
    ("/blog/ceneo-odrzuca-oferty", "0.7", "monthly"),
    ("/regulamin", "0.3", "yearly"),
    ("/polityka-prywatnosci", "0.3", "yearly"),
    ("/polityka-cookies", "0.2", "yearly"),
]


def _format_date(dt) -> str:
    if isinstance(dt, datetime):
        return dt.date().isoformat()
    if isinstance(dt, date):
        return dt.isoformat()
    return date.today().isoformat()


@router.get("/sitemap.xml")
async def sitemap(db: AsyncSession = Depends(get_db)):
    today = date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for path, priority, changefreq in STATIC_ROUTES:
        lines.append("  <url>")
        lines.append(f"    <loc>{SITE}{path}</loc>")
        lines.append(f"    <lastmod>{today}</lastmod>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")

    # Published blog posts from DB
    blog_result = await db.execute(
        select(BlogPost.slug, BlogPost.updated_at, BlogPost.published_at)
        .where(BlogPost.is_published == True)  # noqa: E712
    )
    legacy_blog_slugs = {
        "jak-dodac-produkty-do-ceneo",
        "jak-stworzyc-feed-xml",
        "ceneo-odrzuca-oferty",
    }
    for slug, updated_at, published_at in blog_result.all():
        if slug in legacy_blog_slugs:
            continue  # already in static list
        lastmod = _format_date(updated_at or published_at)
        lines.append("  <url>")
        lines.append(f"    <loc>{SITE}/blog/{escape(slug)}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("    <changefreq>monthly</changefreq>")
        lines.append("    <priority>0.6</priority>")
        lines.append("  </url>")

    # Published landing pages from DB
    landing_result = await db.execute(
        select(LandingPage.slug, LandingPage.updated_at, LandingPage.is_indexable)
        .where(LandingPage.is_published == True)  # noqa: E712
    )
    for slug, updated_at, is_indexable in landing_result.all():
        if not is_indexable:
            continue
        lastmod = _format_date(updated_at)
        lines.append("  <url>")
        lines.append(f"    <loc>{SITE}/p/{escape(slug)}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("    <changefreq>weekly</changefreq>")
        lines.append("    <priority>0.5</priority>")
        lines.append("  </url>")

    lines.append("</urlset>")
    body = "\n".join(lines)
    return Response(content=body, media_type="application/xml")


# ─────────────────────────────────────────────────────────────────────────
# Dynamic HTML rendering for /blog/{slug} and /p/{slug}
# ─────────────────────────────────────────────────────────────────────────

# In-memory cache for the SPA shell template fetched from frontend container
_SHELL_CACHE: dict = {"html": None, "ts": 0.0}
_SHELL_TTL_SECONDS = 60
FRONTEND_INTERNAL_URL = os.getenv("FRONTEND_INTERNAL_URL", "http://frontend:80")


async def _get_shell_template() -> str:
    """Fetch the unmodified SPA shell from frontend container with TTL cache."""
    now = time.time()
    if _SHELL_CACHE["html"] and (now - _SHELL_CACHE["ts"]) < _SHELL_TTL_SECONDS:
        return _SHELL_CACHE["html"]
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{FRONTEND_INTERNAL_URL}/__shell__.html")
            resp.raise_for_status()
            _SHELL_CACHE["html"] = resp.text
            _SHELL_CACHE["ts"] = now
            return resp.text
    except Exception:
        if _SHELL_CACHE["html"]:
            return _SHELL_CACHE["html"]
        raise


def _replace_meta(html: str, attr: str, name: str, value: str) -> str:
    """Replace meta tag value with attribute selector (name= or property=)."""
    pattern = re.compile(rf'<meta {attr}="{re.escape(name)}" content="[^"]*"\s*/>')
    replacement = f'<meta {attr}="{name}" content="{escape(value, quote=True)}" />'
    if pattern.search(html):
        return pattern.sub(replacement, html)
    # Insert before </head> if not present
    return html.replace("</head>", f"  {replacement}\n  </head>")


def _replace_title(html: str, title: str) -> str:
    return re.sub(r"<title>[^<]*</title>", f"<title>{escape(title)}</title>", html)


def _replace_canonical(html: str, url: str) -> str:
    pattern = re.compile(r'<link rel="canonical" href="[^"]*"\s*/>')
    return pattern.sub(f'<link rel="canonical" href="{escape(url, quote=True)}" />', html)


def _strip_jsonld(html: str) -> str:
    html = re.sub(r"<!-- Structured Data:[\s\S]*?</script>\s*", "", html)
    html = re.sub(r'<script type="application/ld\+json">[\s\S]*?</script>\s*', "", html)
    return html


def _inject_jsonld(html: str, blocks: list[dict]) -> str:
    if not blocks:
        return html
    snippets = "\n    ".join(
        f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>'
        for b in blocks
    )
    return html.replace("</head>", f"{snippets}\n  </head>")


SEO_FOOTER = """
        <hr />
        <nav aria-label="Linki Feedy.pl" style="font-size:13px;line-height:1.8;margin-top:30px">
          <strong>Feedy.pl</strong> —
          <a href="/">strona główna</a> ·
          <a href="/blog">blog</a> ·
          <a href="/feed-ceneo">feed Ceneo</a> ·
          <a href="/feed-google-shopping">feed Google Shopping</a> ·
          <a href="/feed-allegro">feed Allegro</a> ·
          <a href="/integracja-shoper">integracja Shoper</a> ·
          <a href="/integracja-woocommerce">integracja WooCommerce</a> ·
          <a href="/porownanie/feedy-vs-datafeedwatch">vs DataFeedWatch</a> ·
          <a href="/oferty/cennik">cennik stron ofert</a> ·
          <a href="/regulamin">regulamin</a> ·
          <a href="/polityka-prywatnosci">polityka prywatności</a>
        </nav>
        <p style="font-size:11px;color:#888;margin-top:10px">© Feedy.pl — Zarządzanie feedami produktowymi dla e-commerce</p>
"""


def _replace_noscript(html: str, body_html: str) -> str:
    pattern = re.compile(r"<noscript>[\s\S]*?</noscript>")
    wrapped = f'<noscript>\n      <div style="max-width:800px;margin:0 auto;padding:40px 20px;font-family:system-ui,sans-serif">\n{body_html}\n{SEO_FOOTER}\n      </div>\n    </noscript>'
    if pattern.search(html):
        return pattern.sub(wrapped, html)
    return html.replace("</body>", f"{wrapped}\n  </body>")


def _build_seo_html(
    *,
    shell: str,
    title: str,
    description: str,
    canonical: str,
    jsonld: list[dict],
    noscript_body: str,
    og_type: str = "website",
    robots: str = "index, follow",
) -> str:
    html = shell
    html = _replace_title(html, title)
    html = _replace_meta(html, "name", "description", description)
    html = _replace_meta(html, "name", "robots", robots)
    html = _replace_canonical(html, canonical)
    html = _replace_meta(html, "property", "og:url", canonical)
    html = _replace_meta(html, "property", "og:title", title)
    html = _replace_meta(html, "property", "og:description", description)
    html = _replace_meta(html, "property", "og:type", og_type)
    html = _replace_meta(html, "name", "twitter:title", title)
    html = _replace_meta(html, "name", "twitter:description", description)
    html = _strip_jsonld(html)
    html = _inject_jsonld(html, jsonld)
    html = _replace_noscript(html, noscript_body)
    return html


def _organization_node() -> dict:
    return {
        "@type": "Organization",
        "name": "Feedy",
        "url": SITE,
        "logo": f"{SITE}/favicon.svg",
    }


def _breadcrumb(items: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": f"{SITE}{path}"}
            for i, (name, path) in enumerate(items)
        ],
    }


# /blog/{slug} — DB blog post HTML render
@router.get("/blog/{slug}", response_class=Response)
async def render_blog_post(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BlogPost).where(BlogPost.slug == slug))
    post = result.scalar_one_or_none()
    if not post or not post.is_published:
        raise HTTPException(status_code=404, detail="Not found")

    canonical = f"{SITE}/blog/{post.slug}"
    title = post.meta_title or f"{post.title} — Blog Feedy"
    description = post.meta_description or post.excerpt or post.title
    robots_parts = []
    robots_parts.append("index" if post.is_indexable else "noindex")
    robots_parts.append("follow" if post.is_followable else "nofollow")
    robots = ", ".join(robots_parts)

    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": post.title,
        "description": description,
        "image": post.hero_image_path or post.og_image_path or f"{SITE}/og-image.svg",
        "author": _organization_node(),
        "publisher": {**_organization_node(), "logo": {"@type": "ImageObject", "url": f"{SITE}/favicon.svg"}},
        "datePublished": (post.published_at or post.created_at).isoformat() if (post.published_at or post.created_at) else None,
        "dateModified": post.updated_at.isoformat() if post.updated_at else None,
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "inLanguage": "pl-PL",
    }
    breadcrumb = _breadcrumb([("Strona główna", "/"), ("Blog", "/blog"), (post.title, f"/blog/{post.slug}")])

    hero_html = ""
    if post.hero_image_path:
        alt = escape(post.hero_image_alt or post.title, quote=True)
        hero_html = f'<figure><img src="{escape(post.hero_image_path, quote=True)}" alt="{alt}" /></figure>'

    excerpt_html = f"<p>{escape(post.excerpt)}</p>" if post.excerpt else ""

    noscript_body = f"""
      <nav><a href="/blog">← Wróć do bloga</a></nav>
      <h1>{escape(post.title)}</h1>
      {excerpt_html}
      {hero_html}
      <div>{post.html}</div>
      <p><a href="/blog">Więcej wpisów na blogu Feedy</a> · <a href="/feed-ceneo">Feed Ceneo</a> · <a href="/feed-google-shopping">Feed Google Shopping</a></p>
    """

    shell = await _get_shell_template()
    html = _build_seo_html(
        shell=shell,
        title=title,
        description=description,
        canonical=canonical,
        jsonld=[article, breadcrumb],
        noscript_body=noscript_body,
        og_type="article",
        robots=robots,
    )
    return Response(content=html, media_type="text/html; charset=utf-8")


# /p/{slug:path} — landing page HTML render
@router.get("/p/{slug:path}", response_class=Response)
async def render_landing_page(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LandingPage).where(LandingPage.slug == slug))
    page = result.scalar_one_or_none()
    if not page or not page.is_published:
        raise HTTPException(status_code=404, detail="Not found")

    canonical = f"{SITE}/p/{page.slug}"
    title = page.meta_title or f"{page.title} — Feedy.pl"
    description = page.meta_description or page.short_description or page.title
    robots_parts = []
    robots_parts.append("index" if page.is_indexable else "noindex")
    robots_parts.append("follow" if page.is_followable else "nofollow")
    robots = ", ".join(robots_parts)

    product_schema: dict = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": page.title,
        "description": description,
        "url": canonical,
    }
    if page.gallery:
        product_schema["image"] = list(page.gallery)[:10]
    elif page.hero_image:
        product_schema["image"] = page.hero_image
    if page.price:
        # Extract first numeric value from free-form price string ("od 199 zł/m²")
        m = re.search(r"\d+(?:[.,]\d+)?", page.price)
        price_value = m.group(0).replace(",", ".") if m else "0"
        product_schema["offers"] = {
            "@type": "Offer",
            "price": price_value,
            "priceCurrency": "PLN",
            "availability": "https://schema.org/InStock",
            "url": canonical,
        }
    elif page.price_negotiable:
        product_schema["offers"] = {
            "@type": "Offer",
            "priceSpecification": {"@type": "PriceSpecification", "valueAddedTaxIncluded": True},
            "availability": "https://schema.org/InStock",
            "url": canonical,
        }

    breadcrumb = _breadcrumb([("Strona główna", "/"), ("Oferty", "/oferty"), (page.title, f"/p/{page.slug}")])

    location_html = f"<p><strong>Lokalizacja:</strong> {escape(page.location)}</p>" if page.location else ""
    price_html = ""
    if page.price:
        price_html = f"<p><strong>Cena:</strong> {escape(page.price)}</p>"
    elif page.price_negotiable:
        price_html = "<p><strong>Cena:</strong> Do wyceny indywidualnej</p>"

    short_html = f"<p>{escape(page.short_description)}</p>" if page.short_description else ""
    full_html = f"<div>{page.full_description}</div>" if page.full_description else ""

    cta_html = ""
    if page.cta_url:
        cta_label = escape(page.cta_text or "Przejdź do oferty!")
        cta_html = f'<p><a href="{escape(page.cta_url, quote=True)}" rel="ugc sponsored nofollow noopener">{cta_label}</a></p>'

    hero_html = ""
    if page.hero_image:
        hero_html = f'<figure><img src="{escape(page.hero_image, quote=True)}" alt="{escape(page.title, quote=True)}" /></figure>'

    noscript_body = f"""
      <h1>{escape(page.title)}</h1>
      {location_html}
      {price_html}
      {short_html}
      {hero_html}
      {full_html}
      {cta_html}
      <p><a href="/">Strona główna Feedy.pl</a> · <a href="/oferty/cennik">Cennik stron ofert</a></p>
    """

    shell = await _get_shell_template()
    html = _build_seo_html(
        shell=shell,
        title=title,
        description=description,
        canonical=canonical,
        jsonld=[product_schema, breadcrumb],
        noscript_body=noscript_body,
        og_type="product",
        robots=robots,
    )
    return Response(content=html, media_type="text/html; charset=utf-8")
