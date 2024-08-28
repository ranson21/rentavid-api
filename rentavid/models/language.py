from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from pydantic import BaseModel

from datetime import datetime

from ..dependencies import Base


class Language(Base):
    __tablename__ = "language"

    language_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, index=True)
    last_update = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class LanguageBase(BaseModel):
    name: str


class LanguageCreate(LanguageBase):
    pass


class LanguageResponse(LanguageBase):
    language_id: int
    last_update: datetime

    class Config:
        orm_mode = True


def get_language(db: Session, language_id: int):
    return db.query(Language).filter(Language.language_id == language_id).first()


def get_languages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Language).offset(skip).limit(limit).all()


def create_language(db: Session, language: LanguageCreate):
    db_language = Language(name=language.name)
    db.add(db_language)
    db.commit()
    db.refresh(db_language)
    return db_language


def update_language(db: Session, language_id: int, language: LanguageCreate):
    db_language = db.query(Language).filter(Language.language_id == language_id).first()
    if db_language:
        db_language.name = language.name
        db.commit()
        db.refresh(db_language)
    return db_language


def delete_language(db: Session, language_id: int):
    db_language = db.query(Language).filter(Language.language_id == language_id).first()
    if db_language:
        db.delete(db_language)
        db.commit()
    return db_language
