from sqlalchemy import Column, Float, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Film(Base):
    __tablename__ = "film"
    film_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    backdrop_path = Column(String)
    poster_path = Column(String)
    release_year = Column(Integer)
    language_id = Column(Integer, ForeignKey("language.language_id"))
    rental_duration = Column(Integer)
    rental_rate = Column(Float)
    length = Column(Integer)
    replacement_cost = Column(Float)
    rating = Column(String)
    last_update = Column(DateTime)
