import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from backend.routes import auth, courses, enrollments, modules, payments, demo

# Load .env — try backend/.env first, then root .env
_here = Path(__file__).parent
load_dotenv(_here / '.env')           # backend/.env
load_dotenv(_here.parent / '.env')    # project root .env (fallback)

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# ─── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(title="Trauma Transformation Institute API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ──────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(modules.router)
app.include_router(payments.router)
app.include_router(demo.router)

# ─── Health ──────────────────────────────────────────────────────────────────
from backend.db_client import noco

@app.get("/api/health")
async def health_check():
    try:
        await noco.get_all("users", params={"limit": 1})
        return {"status": "healthy", "database": "nocodb_connected",
                "env": os.environ.get('VERCEL_ENV', 'development')}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# ─── Global error handler ─────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)})

# ─── Startup log ─────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info("Server started")
    logger.info(f"NOCODB_URL set: {'YES' if os.environ.get('NOCODB_URL') else 'NO'}")
    logger.info(f"NOCODB_TOKEN set: {'YES' if os.environ.get('NOCODB_TOKEN') else 'NO'}")
