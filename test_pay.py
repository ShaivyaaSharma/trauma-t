import asyncio
import logging
logging.basicConfig(level=logging.INFO)

from backend.db_client import noco
from backend.routes.payments import _find_pending_enrollment, _mark_enrollment_paid

async def main():
    session_id = "mock_14bcb11515cb4cafbb7cafd0a5a577f4"
    print(f"Testing session: {session_id}")
    try:
        row = await _find_pending_enrollment(session_id)
        print("Row:", row)
        if row:
            res = await _mark_enrollment_paid(session_id)
            print("Marked paid:", res)
    except Exception as e:
        print("Exception:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
