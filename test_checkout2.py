import asyncio
import os
import httpx
from dotenv import load_dotenv

from backend.db_client import noco
from backend.routes.enrollments import create_checkout, CheckoutRequest

async def main():
    try:
        load_dotenv("backend/.env", override=True)
        users = await noco.get_all("users", params={"limit": 1})
        user = users[0]
        user_id = user.get("userid") or user.get("id")
        
        # take the second course
        courses = await noco.get_all("Courses", params={"limit": 5})
        for c in courses:
            course_id = c.get("course_id")
            
            # check if enrolled
            enrolls = await noco.get_all("enrollments", params={"where": f"(userid,eq,{user_id})~and(course_id,eq,{course_id})~and(payment_status,eq,paid)"})
            if enrolls:
                continue # skip if enrolled
                
            print(f"Testing on course: {course_id}")
            req = CheckoutRequest(course_id=course_id, origin_url="http://localhost:3000")
            res = await create_checkout(req, user)
            print("SUCCESS:", res)
            break
            
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
