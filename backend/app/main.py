from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.limiter import limiter
from app.routers import ai, auth, billing, blog, competitor_prices, feeds_in, feeds_out, images, imports, landing_pages, notifications, organizations, public_feed, seo, value_maps


def create_app() -> FastAPI:
    app = FastAPI(title="Feedy", version="0.1.0")

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

    app.include_router(auth.router)
    app.include_router(billing.router)
    app.include_router(feeds_in.router)
    app.include_router(feeds_out.router)
    app.include_router(organizations.router)
    app.include_router(public_feed.router)
    app.include_router(images.router)
    app.include_router(ai.router)
    app.include_router(value_maps.router)
    app.include_router(blog.router)
    app.include_router(landing_pages.router)
    app.include_router(seo.router)
    app.include_router(notifications.router)
    app.include_router(imports.router)
    app.include_router(competitor_prices.router)

    return app


app = create_app()
