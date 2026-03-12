import os
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

import models
from database import get_db
from cache import ingredient_cache

router = APIRouter(prefix="/admin", tags=["admin"])

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "supersecret-admin-key")


def verify_admin_key(x_admin_key: str = Header(...)):
    if x_admin_key != ADMIN_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin key")


class IngredientCreate(BaseModel):
    name: str
    health_score: float = 0.0
    flags: Optional[str] = None


class IngredientUpdate(BaseModel):
    health_score: Optional[float] = None
    flags: Optional[str] = None


@router.post("/ingredients", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_admin_key)])
def add_ingredient(payload: IngredientCreate, db: Session = Depends(get_db)):
    existing = db.query(models.IngredientData).filter(models.IngredientData.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ingredient already exists")

    ingredient = models.IngredientData(
        name=payload.name,
        health_score=payload.health_score,
        flags=payload.flags,
    )
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)

    # Clear any stale cache entry for this name
    cache_key = payload.name.strip().lower()
    ingredient_cache.pop(cache_key, None)

    return {"id": ingredient.id, "name": ingredient.name, "health_score": ingredient.health_score, "flags": ingredient.flags}


@router.put("/ingredients/{id}", dependencies=[Depends(verify_admin_key)])
def update_ingredient(id: int, payload: IngredientUpdate, db: Session = Depends(get_db)):
    ingredient = db.query(models.IngredientData).filter(models.IngredientData.id == id).first()
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")

    if payload.health_score is not None:
        ingredient.health_score = payload.health_score
    if payload.flags is not None:
        ingredient.flags = payload.flags

    db.commit()
    db.refresh(ingredient)

    # Clear stale cache entry
    cache_key = ingredient.name.strip().lower()
    ingredient_cache.pop(cache_key, None)

    return {"id": ingredient.id, "name": ingredient.name, "health_score": ingredient.health_score, "flags": ingredient.flags}


@router.delete("/ingredients/{id}", status_code=status.HTTP_200_OK, dependencies=[Depends(verify_admin_key)])
def delete_ingredient(id: int, db: Session = Depends(get_db)):
    ingredient = db.query(models.IngredientData).filter(models.IngredientData.id == id).first()
    if not ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")

    cache_key = ingredient.name.strip().lower()
    db.delete(ingredient)
    db.commit()

    # Clear stale cache entry
    ingredient_cache.pop(cache_key, None)

    return {"detail": f"Ingredient '{cache_key}' deleted successfully"}
