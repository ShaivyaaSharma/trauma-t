"""
Payment routes:
  GET  /api/payments/status/{session_id}  — frontend polls this after Stripe redirect
  POST /api/payments/webhook/stripe        — Stripe sends payment events here

Sandbox/demo mode
─────────────────
• Real Stripe key (sk_test_... / sk_live_...): status verified via Stripe API.
• Mock session IDs (prefix "mock_"): auto-confirmed as paid for demo purposes.
• Webhook endpoint remains active; register it in Stripe Dashboard for production.
"""
import json
import os
import logging

import stripe

from fastapi import APIRouter, HTTPException, Depends, Request, Response
from backend.db_client import noco
from backend.routes.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments")

STRIPE_API_KEY        = os.environ.get("STRIPE_API_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")


def _is_real_stripe_key(key: str) -> bool:
    return (key.startswith("sk_test_") or key.startswith("sk_live_")) and len(key) > 24

STRIPE_AVAILABLE = _is_real_stripe_key(STRIPE_API_KEY)

if STRIPE_AVAILABLE:
    stripe.api_key = STRIPE_API_KEY


# ── Helpers ──────────────────────────────────────────────────────────────────

async def _find_pending_enrollment(session_id: str) -> dict | None:
    """
    Find a pending enrollment for this session_id.
    Scans progress_data JSON.
    """
    rows = await noco.get_all("enrollments", params={
        "where": "(payment_status,eq,pending)",
        "limit": 200,
    })
    for r in rows:
        progress = json.loads(r.get("progress_data") or "{}")
        if progress.get("session_id") == session_id:
            return r
    return None


async def _mark_enrollment_paid(session_id: str) -> bool:
    """Mark a pending enrollment as paid. Returns True if a row was updated."""
    row = await _find_pending_enrollment(session_id)
    if not row:
        return False
    row_id = row.get("Id") or row.get("id")
    await noco.update_by_id("enrollments", row_id, {"payment_status": "paid"})
    logger.info(f"Enrollment {row_id} marked paid (session {session_id})")
    return True


# ── Routes ───────────────────────────────────────────────────────────────────

@router.get("/status/{session_id}")
async def get_payment_status(session_id: str, user: dict = Depends(get_current_user)):
    """
    Poll endpoint — called by PaymentSuccessPage every 2 s after Stripe redirect.
    Returns { status, payment_status }.
    """

    # ── Mock session: auto-confirm ───────────────────────────────────────────
    if session_id.startswith("mock_"):
        await _mark_enrollment_paid(session_id)
        return {"status": "complete", "payment_status": "paid"}

    # ── Real Stripe session ──────────────────────────────────────────────────
    if not STRIPE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Stripe API key not configured. Set STRIPE_API_KEY=sk_test_... in backend/.env"
        )

    try:
        stripe.api_key = STRIPE_API_KEY
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    payment_status = session.get("payment_status", "unpaid")  # "paid" | "unpaid"
    status         = session.get("status", "open")             # "open" | "complete" | "expired"

    if payment_status == "paid":
        await _mark_enrollment_paid(session_id)
        return {"status": "complete", "payment_status": "paid"}

    if status == "expired":
        return {"status": "expired", "payment_status": "unpaid"}

    return {"status": status, "payment_status": payment_status}


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """
    Stripe sends checkout.session.completed here. Register this URL in
    Stripe Dashboard → Developers → Webhooks for reliable server-side confirmation.
    """
    payload    = await request.body()
    sig_header = request.headers.get("Stripe-Signature", "")

    if STRIPE_WEBHOOK_SECRET:
        try:
            stripe.api_key = STRIPE_API_KEY
            event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        except stripe.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid webhook signature")
    else:
        # No secret configured — parse without verification (OK for local dev)
        import json as _json
        try:
            event = _json.loads(payload)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = event.get("type", "")
    logger.info(f"Stripe webhook event: {event_type}")

    if event_type == "checkout.session.completed":
        session    = event["data"]["object"]
        session_id = session.get("id", "")
        pmt_status = session.get("payment_status", "")
        if pmt_status == "paid":
            await _mark_enrollment_paid(session_id)

    return Response(content='{"received":true}', media_type="application/json")
