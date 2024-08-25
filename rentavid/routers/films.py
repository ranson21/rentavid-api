from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from typing import List, Optional
from datetime import datetime

from ..dependencies import get_db
from ..models.film import Film


router = APIRouter()


class FilmBase(BaseModel):
    title: str
    description: Optional[str] = None
    backdrop_path: Optional[str] = None
    poster_path: Optional[str] = None
    description: Optional[str] = None
    release_year: Optional[int] = None
    language_id: int
    rental_duration: int
    rental_rate: float
    length: Optional[int] = None
    replacement_cost: float
    rating: Optional[str] = None


class FilmCreate(FilmBase):
    pass


class FilmResponse(FilmBase):
    film_id: int
    last_update: datetime

    class Config:
        orm_mode = True


# Film endpoints
@router.post("/films/", response_model=FilmResponse)
def create_film(film: FilmCreate, db: Session = Depends(get_db)):
    db_film = Film(**film.dict(), last_update=datetime.now())
    db.add(db_film)
    db.commit()
    db.refresh(db_film)
    return db_film


@router.get("/films/", response_model=List[FilmResponse])
def read_films(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    films = db.query(Film).offset(skip).limit(limit).all()
    return films


@router.get("/films/{film_id}", response_model=FilmResponse)
def read_film(film_id: int, db: Session = Depends(get_db)):
    film = db.query(Film).filter(Film.film_id == film_id).first()
    if film is None:
        raise HTTPException(status_code=404, detail="Film not found")
    return film
