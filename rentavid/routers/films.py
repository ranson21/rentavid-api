from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from sqlalchemy.sql.expression import func
from sqlalchemy import case, func, desc, or_
from math import ceil


from typing import List, Optional
from datetime import datetime

from ..dependencies import get_db
from ..models.film import Film
from ..models.category import FilmCategory


router = APIRouter()


class FilmBase(BaseModel):
    film_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    backdrop_path: Optional[str] = None
    poster_path: Optional[str] = None
    description: Optional[str] = None
    release_year: Optional[int] = None
    rental_duration: Optional[int] = None
    language_id: Optional[int] = None
    rental_rate: Optional[float] = None
    rating: Optional[str] = None
    replacement_cost: Optional[float] = None
    length: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class FilmCreate(FilmBase):
    pass


class PaginationInfo(BaseModel):
    total_items: int
    page: int
    page_size: int
    total_pages: int


class FilmList(FilmBase):
    pagination: PaginationInfo
    films: List[FilmBase]


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


@router.get("/films", response_model=FilmList)
def read_films(
    db: Session = Depends(get_db),
    release_year: Optional[int] = Query(None),
    languages: Optional[List[int]] = Query(None),
    rental_rate: Optional[float] = Query(None),
    rating: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    query = db.query(Film)

    # Apply filters
    if release_year:
        query = query.filter(Film.release_year == release_year)
    if languages:
        query = query.filter(Film.language_id.in_(languages))
    if rental_rate:
        query = query.filter(Film.rental_rate <= rental_rate)
    if rating:
        query = query.filter(Film.rating == rating)

    # Apply sorting
    if sort_by:
        if sort_by.startswith("-"):
            query = query.order_by(getattr(Film, sort_by[1:]).desc())
        else:
            query = query.order_by(getattr(Film, sort_by))

    # Get total count
    total_items = query.count()

    # Calculate pagination
    total_pages = ceil(total_items / limit)
    offset = (page - 1) * limit

    # Apply pagination
    films = query.offset(offset).limit(limit).all()

    # Convert SQLAlchemy objects to dictionaries
    film_dicts = []
    for film in films:
        film_dict = {
            "film_id": film.film_id,
            "title": film.title,
            "release_year": film.release_year,
            "language_id": film.language_id,
            "rental_rate": film.rental_rate,
            "rating": film.rating,
            "replacement_cost": film.replacement_cost,
            "poster_path": film.poster_path,
            "backdrop_path": film.backdrop_path,
            "rental_duration": film.rental_duration,
            # Add any other fields that are in your Film model
        }
        film_dicts.append(film_dict)

    # Create pagination info
    pagination_info = PaginationInfo(
        total_items=total_items, page=page, page_size=limit, total_pages=total_pages
    )

    return FilmList(pagination=pagination_info, films=film_dicts)


@router.get("/films/{film_id}", response_model=FilmResponse)
def read_film(film_id: int, db: Session = Depends(get_db)):
    film = db.query(Film).filter(Film.film_id == film_id).first()
    if film is None:
        raise HTTPException(status_code=404, detail="Film not found")
    return film
