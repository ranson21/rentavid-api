from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy.sql.expression import func
from sqlalchemy import case, func, desc, or_


from typing import List, Optional
from datetime import datetime

from ..dependencies import get_db
from ..models.film import Film
from ..models.category import FilmCategory


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
@router.get("/films/{film_id}/related", response_model=List[FilmResponse])
def get_related_films(film_id: int, db: Session = Depends(get_db)):
    # First, get the film and its categories
    film = db.query(Film).filter(Film.film_id == film_id).first()
    if film is None:
        raise HTTPException(status_code=404, detail="Film not found")

    # Get the category IDs for this film
    category_ids = [fc.category_id for fc in film.categories]

    # Query for related films
    related_films = (
        db.query(Film)
        .join(FilmCategory)
        .filter(FilmCategory.category_id.in_(category_ids))
        .filter(Film.film_id != film_id)  # Exclude the original film
        .group_by(Film.film_id)
        .order_by(func.count(FilmCategory.category_id).desc(), func.random())
        .limit(10)
        .all()
    )

    return related_films


@router.get("/films/search", response_model=List[FilmResponse])
def search_films(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Number of results to return"),
    db: Session = Depends(get_db),
):
    # Split the query string into words
    search_terms = q.split()

    # Create the base query
    query = db.query(Film)

    # Add search conditions
    conditions = []
    for term in search_terms:
        conditions.append(Film.title.ilike(f"%{term}%"))

    query = query.filter(or_(*conditions))

    # Create a case statement for each search term
    relevance_cases = [
        case((Film.title.ilike(f"%{term}%"), 1), else_=0).label(f"match_{i}")
        for i, term in enumerate(search_terms)
    ]

    # Sum up all the case statements to get the total relevance score
    relevance_score = sum(relevance_cases).label("relevance")

    # Add the relevance score to the query
    query = query.add_columns(relevance_score)

    # Order by the relevance score (descending) and then by title
    query = query.order_by(desc("relevance"), Film.title)

    # Limit the results
    films = query.limit(limit).all()

    if not films:
        raise HTTPException(status_code=404, detail="No films found matching the query")

    # Extract just the Film objects from the result tuples
    films = [film[0] for film in films]

    return films


@router.get("/featured-films/", response_model=List[FilmResponse])
def get_featured_films(db: Session = Depends(get_db)):
    featured_films = db.query(Film).order_by(func.random()).limit(5).all()
    return featured_films


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
