from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from typing import List

from ..dependencies import get_db
from ..models import language


router = APIRouter()


@router.post("/languages/", response_model=language.LanguageResponse)
def create_language(language: language.LanguageCreate, db: Session = Depends(get_db)):
    return language.create_language(db=db, language=language)


@router.get("/languages/", response_model=List[language.LanguageResponse])
def read_languages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    languages = language.get_languages(db, skip=skip, limit=limit)
    return languages


@router.get("/languages/{language_id}", response_model=language.LanguageResponse)
def read_language(language_id: int, db: Session = Depends(get_db)):
    db_language = language.get_language(db, language_id=language_id)
    if db_language is None:
        raise HTTPException(status_code=404, detail="Language not found")
    return db_language


@router.put("/languages/{language_id}", response_model=language.LanguageResponse)
def update_language(
    language_id: int,
    language: language.LanguageCreate,
    db: Session = Depends(get_db),
):
    db_language = language.update_language(
        db, language_id=language_id, language=language
    )
    if db_language is None:
        raise HTTPException(status_code=404, detail="Language not found")
    return db_language


@router.delete("/languages/{language_id}", response_model=language.LanguageResponse)
def delete_language(language_id: int, db: Session = Depends(get_db)):
    db_language = language.delete_language(db, language_id=language_id)
    if db_language is None:
        raise HTTPException(status_code=404, detail="Language not found")
    return db_language
