from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..dependencies import Base


class Actor(Base):
    __tablename__ = "actor"

    actor_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    last_update = Column(DateTime, nullable=False)

    films = relationship("FilmActor", back_populates="actor")


class FilmActor(Base):
    __tablename__ = "film_actor"

    film_id = Column(Integer, ForeignKey("film.film_id"), primary_key=True)
    actor_id = Column(Integer, ForeignKey("actor.actor_id"), primary_key=True)
    last_update = Column(DateTime, nullable=False)

    film = relationship("Film", back_populates="actors")
    actor = relationship("Actor", back_populates="films")
