import asyncio, httpx, os, json
from backend.routes.auth import create_token
from dotenv import load_dotenv

load_dotenv('backend/.env')

async def main():
    # Make a dummy token for the user that was in the db
    # User ID: 0621c457-ef05-4e4c-b3d9-af8576ee532d
    token = create_token("0621c457-ef05-4e4c-b3d9-af8576ee532d", "dummy@example.com")
    
    async with httpx.AsyncClient() as c:
        for cid in ["ett-foundational-001", "hospitality-001", "cctsi-001"]:
            print(f"Checkout for {cid}")
            res = await c.post(
                "http://localhost:8001/api/enrollments/checkout",
                json={"course_id": cid, "origin_url": "http://localhost:3000"},
                headers={"Authorization": f"Bearer {token}"}
            )
            print("Status:", res.status_code)
            print("Body:", res.text)
            print()
            
asyncio.run(main())
