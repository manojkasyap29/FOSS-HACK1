from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

import models
from database import get_db
from auth import get_current_user
from report_generator import generate_scan_report_pdf

router = APIRouter()


@router.get("/history/{user_id}")
def get_scan_history(
    user_id: int, 
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    total_count = db.query(models.ScanHistory).filter(models.ScanHistory.user_id == user_id).count()

    history = (
        db.query(models.ScanHistory)
        .filter(models.ScanHistory.user_id == user_id)
        .order_by(models.ScanHistory.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": entry.id,
                "product_name": entry.product_name,
                "health_score": entry.health_score,
                "verdict": entry.verdict,
                "created_at": entry.created_at,
            }
            for entry in history
        ]
    }


@router.get("/history/{user_id}/export")
def export_scan_history_pdf(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    history = (
        db.query(models.ScanHistory)
        .filter(models.ScanHistory.user_id == user_id)
        .order_by(models.ScanHistory.created_at.desc())
        .all()
    )

    scan_data = [
        {
            "product_name": entry.product_name,
            "health_score": entry.health_score,
            "verdict": entry.verdict,
            "created_at": entry.created_at,
            "ingredients": [
                {"name": ing.name, "flags": ing.flags}
                for ing in entry.ingredients
            ],
        }
        for entry in history
    ]

    pdf_bytes = generate_scan_report_pdf(user_id, scan_data)

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=nutriscan_report_{user_id}.pdf"
        },
    )
