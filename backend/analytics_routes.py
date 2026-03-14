from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List

import models
from database import get_db

router = APIRouter()

@router.get("/analytics/{user_id}")
def get_user_analytics(
    user_id: int, 
    page: int = 1,
    page_size: int = 5,
    db: Session = Depends(get_db)
):
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1. Average health score
    avg_score = db.query(func.avg(models.ScanHistory.health_score)).filter(
        models.ScanHistory.user_id == user_id
    ).scalar()

    # 2. Count of verdicts
    verdict_counts_query = db.query(
        models.ScanHistory.verdict, 
        func.count(models.ScanHistory.id)
    ).filter(
        models.ScanHistory.user_id == user_id
    ).group_by(
        models.ScanHistory.verdict
    ).all()

    verdict_summary = {
        "Healthy": 0,
        "Moderate": 0,
        "Unhealthy": 0
    }
    
    for verdict, count in verdict_counts_query:
        # Map to known keys to ensure consistency
        v_str = str(verdict)
        verdict_summary[v_str] = count

    # 3. Top frequently encountered bad ingredients based on scans
    # Bad ingredients = health_score < 0
    
    # Total count for pagination
    total_bad_count = (
        db.query(models.IngredientData.name)
        .join(models.scan_ingredients_association, models.scan_ingredients_association.c.ingredient_id == models.IngredientData.id)
        .join(models.ScanHistory, models.ScanHistory.id == models.scan_ingredients_association.c.scan_id)
        .filter(models.ScanHistory.user_id == user_id)
        .filter(models.IngredientData.health_score < 0.0)
        .distinct()
        .count()
    )

    bad_ingredients_query = (
        db.query(
            models.IngredientData.name,
            func.count(models.scan_ingredients_association.c.scan_id).label("freq")
        )
        .join(models.scan_ingredients_association, models.scan_ingredients_association.c.ingredient_id == models.IngredientData.id)
        .join(models.ScanHistory, models.ScanHistory.id == models.scan_ingredients_association.c.scan_id)
        .filter(models.ScanHistory.user_id == user_id)
        .filter(models.IngredientData.health_score < 0.0)
        .group_by(models.IngredientData.name)
        .order_by(desc("freq"))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    top_bad_ingredients = [
        {"name": name, "count": freq}
        for name, freq in bad_ingredients_query
    ]

    return {
        "average_health_score": round(avg_score, 2) if avg_score is not None else 0.0,
        "verdict_counts": verdict_summary,
        "top_bad_ingredients": {
            "total_count": total_bad_count,
            "page": page,
            "page_size": page_size,
            "items": top_bad_ingredients
        }
    }
