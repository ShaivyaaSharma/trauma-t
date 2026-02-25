import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")

async def test_update():
    table_id = os.environ.get("NOCODB_TABLE_ENROLLMENTS")
    token = os.environ.get("NOCODB_TOKEN")
    base = "https://app.nocodb.com/api/v2/tables"
    
    url = f"{base}/{table_id}/records"
    headers = {"xc-token": token, "Content-Type": "application/json"}
    
    # Try the correct NocoDB v2 way: pass Id in the body
    async with httpx.AsyncClient() as client:
        res = await client.patch(url, headers=headers, json={"Id": 4, "payment_status": "paid"})
        print(res.status_code)
        print(res.text)

asyncio.run(test_update())
