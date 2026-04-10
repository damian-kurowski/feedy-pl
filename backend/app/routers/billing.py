import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.billing import CheckoutRequest, CheckoutResponse, PortalResponse

router = APIRouter(prefix="/api/billing", tags=["billing"])

PLAN_PRICE_MAP = {
    2: "stripe_price_starter",
    3: "stripe_price_pro",
    4: "stripe_price_business",
}


def _get_price_id(plan_id: int) -> str:
    attr = PLAN_PRICE_MAP.get(plan_id)
    if not attr:
        return ""
    return getattr(settings, attr, "")


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    body: CheckoutRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not settings.stripe_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Płatności nie są jeszcze skonfigurowane. Skontaktuj się z nami.",
        )

    stripe.api_key = settings.stripe_secret_key

    price_id = _get_price_id(body.plan_id)
    if not price_id:
        raise HTTPException(status_code=400, detail="Nieprawidłowy plan")

    if not user.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email)
        user.stripe_customer_id = customer.id
        await db.commit()

    frontend_url = settings.cors_origins.split(",")[0]

    session = stripe.checkout.Session.create(
        customer=user.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=f"{frontend_url}/dashboard?billing=success",
        cancel_url=f"{frontend_url}/dashboard?billing=cancel",
        metadata={"user_id": str(user.id), "plan_id": str(body.plan_id)},
    )
    return CheckoutResponse(checkout_url=session.url)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, settings.stripe_webhook_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session_data = event["data"]["object"]
        user_id = int(session_data["metadata"]["user_id"])
        plan_id = int(session_data["metadata"]["plan_id"])
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.plan_id = plan_id
            await db.commit()

    elif event["type"] == "customer.subscription.deleted":
        customer_id = event["data"]["object"]["customer"]
        result = await db.execute(
            select(User).where(User.stripe_customer_id == customer_id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.plan_id = 1
            await db.commit()

    return {"status": "ok"}


@router.get("/portal", response_model=PortalResponse)
async def billing_portal(
    user: User = Depends(get_current_user),
):
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Płatności nie są jeszcze skonfigurowane.")

    if not user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="Brak aktywnej subskrypcji")

    stripe.api_key = settings.stripe_secret_key
    frontend_url = settings.cors_origins.split(",")[0]

    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=f"{frontend_url}/dashboard",
    )
    return PortalResponse(portal_url=session.url)
