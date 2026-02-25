import os
import pymongo
from datetime import datetime, timezone

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["tti_db"]

user_id = "a67c6ee5-a2bb-4346-8cb6-fc6c3ef7556b"
course_id = "b81e526f-d9ab-4f5b-aa35-692373f18399"

enrollment = {
    "id": "demo-enrollment-id",
    "user_id": user_id,
    "course_id": course_id,
    "payment_status": "paid",
    "session_id": None,
    "enrolled_at": datetime.now(timezone.utc).isoformat()
}

db.enrollments.insert_one(enrollment)
print("Demo user successfully enrolled!")
