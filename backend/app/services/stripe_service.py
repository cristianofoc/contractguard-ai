"""
Stripe payment service.

Provides:
- Customer creation
- PaymentIntent creation (pay-per-use)
- Webhook event handling
"""

import stripe as stripe_lib

from app.config import settings

# Configure the Stripe SDK with the secret key from settings
stripe_lib.api_key = settings.STRIPE_SECRET_KEY


def create_customer(email: str) -> str:
    """
    Create a Stripe customer for the given email address.

    Returns:
        The Stripe customer ID (e.g. "cus_xxx").
    """
    customer = stripe_lib.Customer.create(
        email=email,
        description=f"ContractGuard AI customer — {email}",
    )
    return customer["id"]


def create_payment_intent(customer_id: str, amount_cents: int | None = None) -> str:
    """
    Create a Stripe PaymentIntent for a pay-per-use contract analysis.

    Args:
        customer_id: Stripe customer ID obtained from create_customer().
        amount_cents: Amount in cents. Defaults to the configured price.

    Returns:
        The PaymentIntent client_secret used by the frontend Stripe.js SDK.
    """
    if amount_cents is None:
        amount_cents = settings.PAY_PER_USE_PRICE_CENTS

    intent = stripe_lib.PaymentIntent.create(
        amount=amount_cents,
        currency="usd",
        customer=customer_id,
        metadata={"product": "contract_analysis"},
        automatic_payment_methods={"enabled": True},
    )
    return intent["client_secret"]


def handle_webhook(payload: bytes, sig_header: str) -> dict:
    """
    Verify and parse an incoming Stripe webhook event.

    Args:
        payload: Raw request body bytes (must not be decoded).
        sig_header: Value of the Stripe-Signature HTTP header.

    Returns:
        Parsed Stripe event dict.

    Raises:
        stripe.error.SignatureVerificationError: If signature is invalid.
        ValueError: If the webhook secret is not configured.
    """
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise ValueError("STRIPE_WEBHOOK_SECRET is not configured")

    event = stripe_lib.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )
    return event


def process_payment_succeeded(event: dict) -> str | None:
    """
    Extract the customer ID from a payment_intent.succeeded event.

    Returns:
        Stripe customer ID if present, else None.
    """
    payment_intent = event.get("data", {}).get("object", {})
    return payment_intent.get("customer")
