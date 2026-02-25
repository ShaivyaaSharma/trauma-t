import uuid
import json
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends

from backend.db_client import noco
from backend.routes.auth import get_current_user
from backend.course_content import COURSE_CONTENT

router = APIRouter(prefix="/api/courses")


def _normalize(course: dict) -> dict:
    """Make NocoDB course rows compatible with frontend (adds 'id' alias for course_id)."""
    if course and "course_id" in course and "id" not in course:
        course["id"] = course["course_id"]
    return course


@router.get("")
async def get_courses(track: Optional[str] = None):
    courses = await noco.get_all("Courses", params={"limit": 100})
    if track:
        # 'both' track courses appear in both wellness and clinical
        courses = [c for c in courses if c.get("track") in (track, "both")]
    courses = [_normalize(c) for c in courses]
    courses.sort(key=lambda c: 1 if c.get("is_coming_soon") else 0)
    return courses


@router.get("/{course_id}")
async def get_course(course_id: str):
    course = await noco.find_one("Courses", f"(course_id,eq,{course_id})")
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return _normalize(course)


@router.get("/{course_id}/curriculum")
async def get_curriculum(course_id: str):
    """Return module list (without quiz answers) for the course details page."""
    content = COURSE_CONTENT.get(course_id)
    if not content:
        return []
    # Strip quiz correct_answer before returning to public endpoint
    safe_modules = []
    for mod in content["modules"]:
        m = {k: v for k, v in mod.items() if k != "quiz"}
        safe_modules.append(m)
    return safe_modules


@router.post("")
async def create_course(course_data: dict):
    course_id = str(uuid.uuid4())
    doc = {
        "course_id": course_id,
        **course_data,
    }
    result = await noco.insert_one("Courses", doc)
    return _normalize(result)
