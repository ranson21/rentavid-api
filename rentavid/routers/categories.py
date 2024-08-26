from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime

from ..models.category import FilmCategory, Category
from ..models.film import Film
from ..routers.films import FilmResponse
from ..dependencies import get_db

router = APIRouter()


# Pydantic Models
class FilmCategoryBase(BaseModel):
    film_id: int
    category_id: int


class FilmCategoryCreate(FilmCategoryBase):
    pass


class FilmCategoryResponse(FilmCategoryBase):
    last_update: datetime

    class Config:
        orm_mode = True


class CategoryBase(BaseModel):
    name: str


class CategoryResponse(CategoryBase):
    category_id: int
    name: str

    class Config:
        orm_mode = True


@router.post("/film-categories/", response_model=FilmCategoryResponse)
def create_film_category(
    film_category: FilmCategoryCreate, db: Session = Depends(get_db)
):
    db_film_category = FilmCategory(**film_category.dict(), last_update=datetime.now())
    db.add(db_film_category)
    db.commit()
    db.refresh(db_film_category)
    return db_film_category


@router.get("/film-categories/", response_model=List[FilmCategoryResponse])
def read_film_categories(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    film_categories = db.query(FilmCategory).offset(skip).limit(limit).all()
    return film_categories


@router.get("/films/{film_id}/categories", response_model=List[CategoryResponse])
def read_film_categories(film_id: int, db: Session = Depends(get_db)):
    film = db.query(Film).filter(Film.film_id == film_id).first()
    if film is None:
        raise HTTPException(status_code=404, detail="Film not found")
    return [fc.category for fc in film.categories]


@router.post("/categories/", response_model=CategoryResponse)
def create_category(category: CategoryBase, db: Session = Depends(get_db)):
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/categories/", response_model=List[CategoryResponse])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = db.query(Category).offset(skip).limit(limit).all()
    return categories


@router.get("/categories/{category_id}", response_model=CategoryResponse)
def read_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int, category: CategoryBase, db: Session = Depends(get_db)
):
    db_category = db.query(Category).filter(Category.category_id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in category.dict().items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/categories/{category_id}", response_model=CategoryResponse)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return category


@router.get("/categories/{category_id}/films", response_model=List[FilmResponse])
def read_category_films(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return [fc.film for fc in category.films]
