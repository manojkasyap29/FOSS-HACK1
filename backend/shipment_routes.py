from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db

router = APIRouter(prefix="/api", tags=["shipments"])


class ShipmentStatusUpdate(BaseModel):
    status: str


@router.get("/shipments")
def list_shipments(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    exporter_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    page = max(1, page)
    page_size = max(1, min(page_size, 100))

    filters = []
    params = {"limit": page_size, "offset": (page - 1) * page_size}

    if status:
        filters.append("s.status = :status")
        params["status"] = status

    if exporter_id is not None:
        filters.append("s.exporter_id = :exporter_id")
        params["exporter_id"] = exporter_id

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    count_sql = text(
        f"""
        SELECT COUNT(*)
        FROM shipments s
        {where_clause}
        """
    )

    data_sql = text(
        f"""
        SELECT
            s.shipment_id,
            s.exporter_id,
            s.status,
            s.created_at,
            u.username AS exporter_name
        FROM shipments s
        LEFT JOIN users u ON u.id = s.exporter_id
        {where_clause}
        ORDER BY s.shipment_id DESC
        LIMIT :limit OFFSET :offset
        """
    )

    try:
        total_count = db.execute(count_sql, params).scalar() or 0
        rows = db.execute(data_sql, params).mappings().all()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query shipments. Ensure tables exist and DATABASE_URL is correct. Error: {str(exc)}",
        )

    items = []
    for row in rows:
        created_at = row.get("created_at")
        created_iso = (
            created_at.isoformat()
            if hasattr(created_at, "isoformat")
            else created_at
        )
        items.append(
            {
                "shipment_id": row.get("shipment_id"),
                "exporter_id": row.get("exporter_id"),
                "exporter_name": row.get("exporter_name"),
                "status": row.get("status"),
                "created_at": created_iso,
            }
        )

    return {
        "total_count": int(total_count),
        "page": page,
        "page_size": page_size,
        "items": items,
    }


@router.get("/shipments/{shipment_id}")
def get_shipment(shipment_id: int, db: Session = Depends(get_db)):
    sql = text(
        """
        SELECT
            s.shipment_id,
            s.exporter_id,
            s.status,
            s.created_at,
            u.username AS exporter_name
        FROM shipments s
        LEFT JOIN users u ON u.id = s.exporter_id
        WHERE s.shipment_id = :shipment_id
        """
    )

    try:
        row = db.execute(sql, {"shipment_id": shipment_id}).mappings().first()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read shipment details. Error: {str(exc)}",
        )

    if not row:
        raise HTTPException(status_code=404, detail="Shipment not found")

    created_at = row.get("created_at")
    created_iso = created_at.isoformat() if hasattr(created_at, "isoformat") else created_at

    return {
        "shipment_id": row.get("shipment_id"),
        "exporter_id": row.get("exporter_id"),
        "exporter_name": row.get("exporter_name"),
        "status": row.get("status"),
        "created_at": created_iso,
    }


@router.get("/shipments/view")
def get_shipment_details_view(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    page = max(1, page)
    page_size = max(1, min(page_size, 100))

    sql = text(
        """
        SELECT *
        FROM shipment_details_view
        LIMIT :limit OFFSET :offset
        """
    )

    try:
        rows = db.execute(
            sql,
            {"limit": page_size, "offset": (page - 1) * page_size},
        ).mappings().all()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query shipment_details_view. Error: {str(exc)}",
        )

    return {
        "page": page,
        "page_size": page_size,
        "items": [dict(row) for row in rows],
    }


@router.put("/shipments/{shipment_id}/status")
def update_shipment_status(
    shipment_id: int,
    payload: ShipmentStatusUpdate,
    db: Session = Depends(get_db),
):
    normalized_status = payload.status.strip()
    if not normalized_status:
        raise HTTPException(status_code=400, detail="status cannot be empty")

    update_sql = text(
        """
        UPDATE shipments
        SET status = :status
        WHERE shipment_id = :shipment_id
        """
    )

    history_sql = text(
        """
        INSERT INTO shipment_history (shipment_id, status, changed_at)
        VALUES (:shipment_id, :status, :changed_at)
        """
    )

    try:
        result = db.execute(
            update_sql,
            {"status": normalized_status, "shipment_id": shipment_id},
        )
        if result.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=404, detail="Shipment not found")

        db.execute(
            history_sql,
            {
                "shipment_id": shipment_id,
                "status": normalized_status,
                "changed_at": datetime.utcnow(),
            },
        )
        db.commit()
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update shipment status using base tables. Error: {str(exc)}",
        )

    return {
        "shipment_id": shipment_id,
        "status": normalized_status,
        "updated_via": "shipments",
    }
