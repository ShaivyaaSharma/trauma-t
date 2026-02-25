"""
Module progress and quiz routes.
Quiz questions are served from backend/course_content.py.
Progress is stored as JSON inside enrollments.progress_data.
"""
import json
import os
import httpx
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List

from backend.db_client import noco
from backend.routes.auth import get_current_user
from backend.course_content import COURSE_CONTENT

router = APIRouter(prefix="/api/courses")

NOCODB_TABLE_ENROLLMENTS = os.environ.get('NOCODB_TABLE_ENROLLMENTS', '')
BASE = "https://app.nocodb.com/api/v2/tables"


class QuizSubmission(BaseModel):
    module_number: int = 0   # optional — already in URL path
    answers: List[int]



async def _get_enrollment_row(user_id: str, course_id: str) -> dict | None:
    """Fetch the paid enrollment row for a user+course."""
    return await noco.find_one("enrollments",
        f"(userid,eq,{user_id})~and(course_id,eq,{course_id})~and(payment_status,eq,paid)")


async def _update_enrollment_progress(row_nocodb_id: int, progress: dict):
    """Patch progress_data JSON on the enrollment row."""
    token = os.environ.get('NOCODB_TOKEN', '')
    table_id = os.environ.get('NOCODB_TABLE_ENROLLMENTS', '')
    url = f"{BASE}/{table_id}/records/{row_nocodb_id}"
    headers = {"xc-token": token, "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        await client.patch(url, headers=headers, json={"progress_data": json.dumps(progress)})


@router.get("/{course_id}/modules")
async def get_course_modules(course_id: str, user: dict = Depends(get_current_user)):
    user_id = user["userid"]
    enrollment = await _get_enrollment_row(user_id, course_id)
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")

    progress = json.loads(enrollment.get("progress_data") or "{}")
    content = COURSE_CONTENT.get(course_id, {"modules": []})

    modules_out = []
    completed = progress.get("completed_modules", [])
    for mod in content["modules"]:
        modules_out.append({
            "module_number": mod["module_number"],
            "title": mod["title"],
            "description": mod["description"],
            "estimated_time": mod.get("estimated_time", "3 hours"),
            "is_completed": mod["module_number"] in completed,
            "is_unlocked": mod["module_number"] == 1 or (mod["module_number"] - 1) in completed,
        })

    return {
        "course_id": course_id,
        "modules": modules_out,
        "completed_modules": completed,
        "current_module": progress.get("current_module", 1),
        "overall_progress": round(len(completed) / max(len(modules_out), 1) * 100, 1)
    }


@router.get("/{course_id}/modules/{module_number}")
async def get_module_detail(course_id: str, module_number: int, user: dict = Depends(get_current_user)):
    user_id = user["userid"]
    enrollment = await _get_enrollment_row(user_id, course_id)
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")

    content = COURSE_CONTENT.get(course_id, {"modules": []})
    mod = next((m for m in content["modules"] if m["module_number"] == module_number), None)
    if not mod:
        raise HTTPException(status_code=404, detail="Module not found")

    # Return module content without quiz answers
    return {k: v for k, v in mod.items() if k != "quiz"}


@router.get("/{course_id}/modules/{module_number}/quiz")
async def get_module_quiz(course_id: str, module_number: int, user: dict = Depends(get_current_user)):
    user_id = user["userid"]
    enrollment = await _get_enrollment_row(user_id, course_id)
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled")

    content = COURSE_CONTENT.get(course_id, {"modules": []})
    mod = next((m for m in content["modules"] if m["module_number"] == module_number), None)
    if not mod:
        raise HTTPException(status_code=404, detail="Module not found")

    questions = mod.get("quiz", [])
    # Strip correct answers before sending to frontend
    safe = [{"question": q["question"], "options": q["options"]} for q in questions]
    return {"module_number": module_number, "questions": safe, "total": len(safe)}


@router.post("/{course_id}/modules/{module_number}/submit-quiz")
async def submit_quiz(course_id: str, module_number: int, submission: QuizSubmission,
                      user: dict = Depends(get_current_user)):
    user_id = user["userid"]

    # Get enrollment with the NocoDB row Id
    token = os.environ.get('NOCODB_TOKEN', '')
    table_id = os.environ.get('NOCODB_TABLE_ENROLLMENTS', '')
    headers = {"xc-token": token, "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{BASE}/{table_id}/records",
            headers=headers,
            params={"where": f"(userid,eq,{user_id})~and(course_id,eq,{course_id})~and(payment_status,eq,paid)"}
        )
        rows = resp.json().get("list", [])
        if not rows:
            raise HTTPException(status_code=403, detail="Not enrolled")
        row = rows[0]
        row_id = row.get("Id") or row.get("id")

    # Grade the quiz
    content = COURSE_CONTENT.get(course_id, {"modules": []})
    mod = next((m for m in content["modules"] if m["module_number"] == module_number), None)
    if not mod:
        raise HTTPException(status_code=404, detail="Module not found")

    questions = mod.get("quiz", [])
    if not questions:
        raise HTTPException(status_code=404, detail="No quiz for this module")
    if len(submission.answers) != len(questions):
        raise HTTPException(status_code=400, detail="Answer count mismatch")

    correct = sum(1 for i, q in enumerate(questions) if submission.answers[i] == q["correct_answer"])
    score = correct / len(questions)
    passed = score >= 0.8

    # Update progress
    progress = json.loads(row.get("progress_data") or "{}")
    completed = progress.get("completed_modules", [])
    if passed and module_number not in completed:
        completed.append(module_number)
        progress["completed_modules"] = completed
        progress["current_module"] = module_number + 1
    progress[f"module_{module_number}_score"] = round(score * 100, 1)

    await _update_enrollment_progress(row_id, progress)

    return {
        "score": round(score * 100, 1),
        "correct": correct,
        "total": len(questions),
        "passed": passed,
        "review": [
            {
                "question": q["question"],
                "your_answer": q["options"][submission.answers[i]],
                "correct_answer": q["options"][q["correct_answer"]],
                "is_correct": submission.answers[i] == q["correct_answer"],
                "explanation": q.get("explanation", "")
            }
            for i, q in enumerate(questions)
        ]
    }
