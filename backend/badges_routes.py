from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import get_db

router = APIRouter(prefix="/badges", tags=["badges"])

# Simple static badges logic for Gamification
BADGES_CRITERIA = {
    "First Scan": {"threshold": 1, "description": "Scanned your first product!"},
    "Healthy Eater": {"threshold": 5, "description": "Scanned 5 healthy products!"},
    "Health Guru": {"threshold": 25, "description": "Scanned 25 healthy products!"},
}

@router.get("/{user_id}")
def get_user_badges(user_id: int, db: Session = Depends(get_db)):
    """
    Returns the badges earned by a user based on their Scan History.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Count total scans
    total_scans = db.query(models.ScanHistory).filter(models.ScanHistory.user_id == user_id).count()
    
    # Count healthy scans
    healthy_scans = db.query(models.ScanHistory).filter(
        models.ScanHistory.user_id == user_id, 
        models.ScanHistory.verdict == "Healthy"
    ).count()

    earned_badges = []

    # Evaluate criteria
    if total_scans >= BADGES_CRITERIA["First Scan"]["threshold"]:
        earned_badges.append({
            "name": "First Scan",
            "description": BADGES_CRITERIA["First Scan"]["description"]
        })

    if healthy_scans >= BADGES_CRITERIA["Healthy Eater"]["threshold"]:
        earned_badges.append({
            "name": "Healthy Eater",
            "description": BADGES_CRITERIA["Healthy Eater"]["description"]
        })
        
    if healthy_scans >= BADGES_CRITERIA["Health Guru"]["threshold"]:
        earned_badges.append({
            "name": "Health Guru",
            "description": BADGES_CRITERIA["Health Guru"]["description"]
        })

    return {
        "user_id": user_id,
        "total_scans": total_scans,
        "healthy_scans": healthy_scans,
        "badges": earned_badges
    }
