from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..dependencies import Base


# SQLAlchemy Models
class FilmCategory(Base):
    __tablename__ = "film_category"
    film_id = Column(Integer, ForeignKey("film.film_id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("category.category_id"), primary_key=True)
    last_update = Column(DateTime, nullable=False)

    film = relationship("Film", back_populates="categories")
    category = relationship("Category", back_populates="films")


class Category(Base):
    __tablename__ = "category"
    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    films = relationship("FilmCategory", back_populates="category")
