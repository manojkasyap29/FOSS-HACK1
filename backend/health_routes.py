from fastapi import APIRouter
from sqlalchemy import text
from database import SessionLocal
import time
import psutil  # pip install psutil

router = APIRouter(tags=["health"])

_start_time = time.time()


@router.get("/health")
def health_check():
    """
    Returns the health status of the API, database, and system resources.
    Useful for monitoring and uptime checks.
    """
    db_status = "ok"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        db_status = f"error: {str(e)}"

    uptime_seconds = round(time.time() - _start_time, 2)
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
        "uptime_seconds": uptime_seconds,
        "cpu_usage_percent": cpu_percent,
        "memory_used_percent": memory.percent,
        "memory_available_mb": round(memory.available / (1024 * 1024), 2),
    }
