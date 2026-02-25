import asyncio, httpx, os, json
from dotenv import load_dotenv

load_dotenv('backend/.env')
base = 'https://app.nocodb.com/api/v2/tables'
table_id = os.environ.get('NOCODB_TABLE_ENROLLMENTS')
token = os.environ.get('NOCODB_TOKEN')
headers = {'xc-token': token, 'Content-Type': 'application/json'}

async def main():
    async with httpx.AsyncClient() as c:
        res_get = await c.get(f'{base}/{table_id}/records?limit=100', headers=headers)
        rows = res_get.json().get('list', [])
        for r in rows:
            row_id = r.get('Id')
            print(f"Deleting row {row_id}...")
            res = await c.request("DELETE", f'{base}/{table_id}/records', headers=headers, json=[row_id])
            print(f"Deleted row {row_id}:", res.status_code)

if __name__ == "__main__":
    asyncio.run(main())
