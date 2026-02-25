"""Demo enrollment endpoint — skips Stripe, creates a paid enrollment directly."""
import json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.db_client import noco
from backend.routes.auth import get_current_user

router = APIRouter(prefix="/api/demo")


class DemoEnrollRequest(BaseModel):
    course_id: str


@router.post("/enroll")
async def demo_enroll(data: DemoEnrollRequest, user: dict = Depends(get_current_user)):
    """Create a paid enrollment directly (demo mode — no Stripe)."""
    course = await noco.find_one("Courses", f"(course_id,eq,{data.course_id})")
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.get("is_coming_soon"):
        raise HTTPException(status_code=400, detail="Course not yet available")

    user_id = user["userid"]

    # Check if already enrolled
    existing = await noco.find_one("enrollments",
        f"(userid,eq,{user_id})~and(course_id,eq,{data.course_id})~and(payment_status,eq,paid)")
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled in this course")

    # Create paid enrollment directly
    await noco.insert_one("enrollments", {
        "userid": user_id,
        "course_id": data.course_id,
        "payment_status": "paid",
        "progress_data": json.dumps({"completed_modules": [], "current_module": 1}),
    })

    return {"status": "enrolled", "course_id": data.course_id}
