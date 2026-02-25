"""
Seeds ALL original courses into NocoDB Courses table.
Run once: python3 backend/seed_nocodb_courses.py
"""
import httpx
import asyncio
import os
import uuid
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

TOKEN = os.environ.get('NOCODB_TOKEN')
TABLE_ID = os.environ.get('NOCODB_TABLE_COURSES')
URL = f"https://app.nocodb.com/api/v2/tables/{TABLE_ID}/records"

# Exact original course data from reassign_tracks.py and sync_courses.py
COURSES = [
    {
        "course_id": "ett-foundational-001",
        "title": "ETT Foundational Course",
        "track": "both",
        "description": "The prerequisite certification for all advanced ETT programs. Learn the foundational principles of Emotional Transformation Therapy.",
        "price": 25000,
        "duration": "6 weeks",
        "location": "Online",
        "schedule": "Weekends",
        "instructor": "Sonia Siddhu",
        "is_coming_soon": False,
    },
    {
        "course_id": "cctsi-001",
        "title": "CCTSI (Certified Clinical Trauma Specialist - Individual)",
        "track": "clinical",
        "description": "Clinical trauma treatment for individual adults.",
        "price": 32000,
        "duration": "8 weeks",
        "location": "Online",
        "schedule": "Tuesdays & Thursdays",
        "instructor": "Senior Clinical Trainer",
        "is_coming_soon": False,
    },
    {
        "course_id": "cctsf-001",
        "title": "CCTSF (Certified Clinical Trauma Specialist - Family)",
        "track": "clinical",
        "description": "Family systems and intergenerational trauma diagnosis.",
        "price": 32000,
        "duration": "8 weeks",
        "location": "Online",
        "schedule": "Sat & Sun",
        "instructor": "Family Systems Expert",
        "is_coming_soon": False,
    },
    {
        "course_id": "cctsa-001",
        "title": "CCTSA (Certified Clinical Trauma Specialist - Addiction)",
        "track": "clinical",
        "description": "Neurobiology of addiction and complex trauma treatment.",
        "price": 35000,
        "duration": "10 weeks",
        "location": "Online",
        "schedule": "Weekly Intensive",
        "instructor": "Addiction Specialist",
        "is_coming_soon": False,
    },
    {
        "course_id": "accts-001",
        "title": "ACCTS (Advanced Certified Clinical Trauma Specialist)",
        "track": "clinical",
        "description": "Complexity, supervision, and advanced diagnostic frameworks.",
        "price": 45000,
        "duration": "12 weeks",
        "location": "Online",
        "schedule": "Custom",
        "instructor": "Institute Director",
        "is_coming_soon": False,
    },
    {
        "course_id": "cctsp-001",
        "title": "CCTS-P (Certified Clinical Trauma Specialist - Prenatal/Pediatric)",
        "track": "clinical",
        "description": "Early developmental trauma and pediatric mental health.",
        "price": 32000,
        "duration": "8 weeks",
        "location": "Online",
        "schedule": "Mondays",
        "instructor": "Pediatric Expert",
        "is_coming_soon": False,
    },
    {
        "course_id": "ctss-001",
        "title": "CTSS (Certified Trauma Support Specialist)",
        "track": "wellness",
        "description": "Trauma awareness and psychological first aid.",
        "price": 15000,
        "duration": "4 weeks",
        "location": "Online",
        "schedule": "Flexi-learning",
        "instructor": "Support Lead",
        "is_coming_soon": False,
    },
    {
        "course_id": "crp-001",
        "title": "CRP (Community Resilience Practitioner)",
        "track": "wellness",
        "description": "Community healing and referral systems.",
        "price": 20000,
        "duration": "6 weeks",
        "location": "Hybrid",
        "schedule": "Bi-weekly",
        "instructor": "Community Lead",
        "is_coming_soon": False,
    },
    {
        "course_id": "hospitality-001",
        "title": "Trauma-Informed Hospitality Training",
        "track": "wellness",
        "description": "Trauma-informed care for hospitality professionals.",
        "price": 12000,
        "duration": "4 weeks",
        "location": "Online",
        "schedule": "Flexi-learning",
        "instructor": "ETT Certified Trainer",
        "is_coming_soon": False,
    },
    {
        "course_id": "retreat-001",
        "title": "Wellness Retreat Program",
        "track": "wellness",
        "description": "Design and facilitate trauma-informed wellness retreats.",
        "price": 18000,
        "duration": "5 weeks",
        "location": "Online",
        "schedule": "Weekends",
        "instructor": "ETT Certified Trainer",
        "is_coming_soon": False,
    },
    {
        "course_id": "rehab-001",
        "title": "Rehabilitation Support Program",
        "track": "clinical",
        "description": "Trauma-informed care in rehabilitation and correctional settings.",
        "price": 22000,
        "duration": "6 weeks",
        "location": "Online",
        "schedule": "Wednesdays",
        "instructor": "ETT Certified Trainer",
        "is_coming_soon": True,
    },
]


async def seed():
    headers = {
        "xc-token": TOKEN,
        "Content-Type": "application/json"
    }
    print(f"Seeding {len(COURSES)} courses to NocoDB...\n")
    async with httpx.AsyncClient(timeout=30.0) as client:
        # First check existing courses to avoid duplicates
        resp = await client.get(URL, headers=headers, params={"limit": 100})
        existing_titles = {r.get("title") for r in resp.json().get("list", [])}

        for course in COURSES:
            if course["title"] in existing_titles:
                print(f"⏭️  Skipped (already exists): {course['title']}")
                continue
            resp = await client.post(URL, headers=headers, json=course)
            if resp.status_code in [200, 201]:
                print(f"✅ Inserted: {course['title']}")
            else:
                print(f"❌ Failed ({resp.status_code}): {course['title']} — {resp.text}")

    print("\n✅ Done! Check your NocoDB Courses table.")


if __name__ == "__main__":
    if not TOKEN or not TABLE_ID:
        print("❌ Missing NOCODB_TOKEN or NOCODB_TABLE_COURSES in backend/.env")
    else:
        asyncio.run(seed())
