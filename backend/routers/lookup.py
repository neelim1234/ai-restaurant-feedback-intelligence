"""
backend/routers/lookup.py - Routing configuration for all metadata lookups.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models.lookup import City, Cuisine
from models.org import Brand, Branch

router = APIRouter(prefix="/api/lookup", tags=["Lookups"])


class LookupItem(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class BranchLookupItem(BaseModel):
    id: int
    name: str
    brand_id: int
    city_id: int

    class Config:
        from_attributes = True


@router.get("/cities", response_model=List[LookupItem])
def get_cities(db: Session = Depends(get_db)):
    """Returns a list of all cities."""
    return db.query(City).order_by(City.name).all()


@router.get("/brands", response_model=List[LookupItem])
def get_brands(db: Session = Depends(get_db)):
    """Returns a list of all brands."""
    return db.query(Brand).order_by(Brand.name).all()


@router.get("/cuisines", response_model=List[LookupItem])
def get_cuisines(db: Session = Depends(get_db)):
    """Returns a list of all cuisines."""
    return db.query(Cuisine).order_by(Cuisine.name).all()


@router.get("/branches", response_model=List[BranchLookupItem])
def get_branches(
    city_id: Optional[int] = Query(None, description="Filter branches by City ID"),
    brand_id: Optional[int] = Query(None, description="Filter branches by Brand ID"),
    db: Session = Depends(get_db)
):
    """Returns a list of branches, optionally filtered by city or brand."""
    query = db.query(Branch)
    if city_id is not None:
        query = query.filter(Branch.city_id == city_id)
    if brand_id is not None:
        query = query.filter(Branch.brand_id == brand_id)
    return query.order_by(Branch.name).all()
