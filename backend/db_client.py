"""
NocoDB v2 API client — reads env vars lazily at request time.

Required environment variables:
  NOCODB_TOKEN             - API token
  NOCODB_TABLE_USERS       - Table ID for users
  NOCODB_TABLE_COURSES     - Table ID for Courses
  NOCODB_TABLE_ENROLLMENTS - Table ID for enrollments
"""
import os
import httpx
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env eagerly here so env vars are available when module is imported
_here = Path(__file__).parent
load_dotenv(_here / '.env')         # backend/.env
load_dotenv(_here.parent / '.env')  # project root .env

logger = logging.getLogger(__name__)

BASE = "https://app.nocodb.com/api/v2/tables"

TABLE_MAP = {
    "users":       "NOCODB_TABLE_USERS",
    "Courses":     "NOCODB_TABLE_COURSES",
    "enrollments": "NOCODB_TABLE_ENROLLMENTS",
}


class NocoDBClient:

    def _token(self) -> str:
        t = os.environ.get('NOCODB_TOKEN', '')
        if not t:
            raise RuntimeError("NOCODB_TOKEN is not set.")
        return t

    def _headers(self) -> dict:
        return {
            "xc-token": self._token(),
            "Content-Type": "application/json"
        }

    def _url(self, table_name: str) -> str:
        env_key = TABLE_MAP.get(table_name)
        if not env_key:
            raise RuntimeError(f"Unknown table: '{table_name}'")
        table_id = os.environ.get(env_key, '')
        if not table_id:
            raise RuntimeError(
                f"Table ID for '{table_name}' not set. Set {env_key} environment variable."
            )
        return f"{BASE}/{table_id}/records"

    async def get_all(self, table_name: str, params: dict = None):
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self._url(table_name),
                headers=self._headers(), params=params)
            if response.status_code != 200:
                logger.error(f"NocoDB Error ({response.status_code}): {response.text}")
                return []
            return response.json().get('list', [])

    async def find_one(self, table_name: str, where_clause: str):
        """where_clause example: '(email,eq,test@test.com)'"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self._url(table_name),
                headers=self._headers(),
                params={"where": where_clause, "limit": 1})
            if response.status_code != 200:
                logger.error(f"NocoDB Error ({response.status_code}): {response.text}")
                return None
            results = response.json().get('list', [])
            return results[0] if results else None

    async def insert_one(self, table_name: str, data: dict):
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self._url(table_name),
                headers=self._headers(), json=data)
            if response.status_code not in [200, 201]:
                logger.error(f"NocoDB Insert Error ({response.status_code}): {response.text}")
                raise Exception(f"Failed to insert into {table_name}: {response.text}")
            return response.json()

    async def update_by_id(self, table_name: str, row_id: int, data: dict):
        payload = {"Id": row_id, **data}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.patch(
                self._url(table_name),
                headers=self._headers(), json=payload)
            if response.status_code not in [200, 201]:
                logger.error(f"NocoDB Update Error ({response.status_code}): {response.text}")
                raise Exception(f"Failed to update {table_name}: {response.text}")
            return response.json()


noco = NocoDBClient()
