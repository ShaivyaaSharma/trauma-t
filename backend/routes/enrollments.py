"""
Enrollment routes:
  GET  /api/enrollments/my       — list paid enrollments for logged-in user
  POST /api/enrollments/checkout — create Stripe Checkout Session (or mock)

Sandbox/demo mode
─────────────────
• Set STRIPE_API_KEY=sk_test_... in backend/.env to use real Stripe test mode.
  Test card: 4242 4242 4242 4242  Exp: any future  CVC: any
• Leave STRIPE_API_KEY empty or as placeholder to use built-in mock checkout
  (auto-confirms after redirect — great for demos without a Stripe account).
"""
import json
import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from backend.db_client import noco
from backend.routes.auth import get_current_user
from backend.course_content import COURSE_CONTENT

router = APIRouter(prefix="/api/enrollments")

# ── Config ───────────────────────────────────────────────────────────────────
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")

# A key is "real" if it begins with sk_test_ or sk_live_  AND  is long enough
# (sk_test_placeholder is NOT a real key — it's only 20 chars; real keys are 50+)
def _is_real_stripe_key(key: str) -> bool:
    return (key.startswith("sk_test_") or key.startswith("sk_live_")) and len(key) > 24

STRIPE_AVAILABLE = _is_real_stripe_key(STRIPE_API_KEY)

if STRIPE_AVAILABLE:
    import stripe
    stripe.api_key = STRIPE_API_KEY


# ── Pydantic models ──────────────────────────────────────────────────────────
class CheckoutRequest(BaseModel):
    course_id: str
    origin_url: str   # e.g. "http://localhost:3000"


# ── Helpers ──────────────────────────────────────────────────────────────────
async def _get_course(course_id: str) -> dict:
    course = await noco.find_one("Courses", f"(course_id,eq,{course_id})")
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.get("is_coming_soon"):
        raise HTTPException(status_code=400, detail="This course is not yet available")
    return course


async def _check_already_enrolled(user_id: str, course_id: str):
    existing = await noco.find_one(
        "enrollments",
        f"(userid,eq,{user_id})~and(course_id,eq,{course_id})~and(payment_status,eq,paid)"
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled in this course")


async def _create_pending_enrollment(user_id: str, course_id: str, session_id: str):
    """Insert a pending enrollment row in NocoDB."""
    await noco.insert_one("enrollments", {
        "userid":         user_id,
        "course_id":      course_id,
        "payment_status": "pending",
        "progress_data":  json.dumps({
            "completed_modules": [],
            "current_module":    1,
            "session_id":        session_id,
        }),
    })


# ── Routes ───────────────────────────────────────────────────────────────────

@router.get("/my")
async def get_my_enrollments(user: dict = Depends(get_current_user)):
    """Return all paid enrollments for the logged-in user with course details."""
    user_id = user["userid"]
    enrollments = await noco.get_all("enrollments", params={
        "where": f"(userid,eq,{user_id})~and(payment_status,eq,paid)",
        "limit": 100,
    })

    result = []
    for enrollment in enrollments:
        course = await noco.find_one("Courses", f"(course_id,eq,{enrollment.get('course_id', '')})")
        if course:
            course["id"] = course.get("course_id", "")

        progress = json.loads(enrollment.get("progress_data") or "{}")
        content  = COURSE_CONTENT.get(enrollment.get("course_id", ""), {"modules": []})

        result.append({
            "enrollment": {
                "id":                enrollment.get("Id") or enrollment.get("id", ""),
                "course_id":         enrollment.get("course_id", ""),
                "payment_status":    enrollment.get("payment_status", ""),
                "completed_modules": len(progress.get("completed_modules", [])),
                "total_modules":     len(content["modules"]),
            },
            "course": course or {},
        })

    return result


@router.post("/checkout")
async def create_checkout(
    checkout_data: CheckoutRequest,
    user: dict = Depends(get_current_user),
):
    """
    Create a Stripe Checkout Session (real or mock).
    Returns { checkout_url, session_id }.
    """
    course   = await _get_course(checkout_data.course_id)
    user_id  = user["userid"]

    await _check_already_enrolled(user_id, checkout_data.course_id)

    price_inr    = int(float(course.get("price", 0)))
    amount_paise = price_inr * 100   # Stripe INR uses paise (1 INR = 100 paise)

    success_url = f"{checkout_data.origin_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url  = f"{checkout_data.origin_url}/courses/{checkout_data.course_id}"

    # ── Real Stripe ──────────────────────────────────────────────────────────
    if STRIPE_AVAILABLE:
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "inr",
                        "unit_amount": amount_paise,
                        "product_data": {
                            "name":        course.get("title", "Course Enrollment"),
                            "description": course.get("description", ""),
                        },
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=user.get("email"),
                metadata={
                    "user_id":     str(user_id),
                    "user_email":  user.get("email", ""),
                    "course_id":   checkout_data.course_id,
                    "course_title": course.get("title", ""),
                },
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        session_id   = session.id
        checkout_url = session.url

    # ── Mock / Demo checkout ─────────────────────────────────────────────────
    else:
        import urllib.parse
        session_id   = f"mock_{uuid.uuid4().hex}"
        success_enc  = urllib.parse.quote(success_url)
        # Redirect to the frontend Mock Checkout Gateway
        checkout_url = (
            f"{checkout_data.origin_url}/checkout-mock"
            f"?session_id={session_id}&success_url={success_enc}&mock=1"
        )

    await _create_pending_enrollment(user_id, checkout_data.course_id, session_id)

    return {"checkout_url": checkout_url, "session_id": session_id}
