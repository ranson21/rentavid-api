from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from typing import List
from datetime import datetime

from ..dependencies import get_db
from ..models.actor import Actor, FilmActor
from ..models.film import Film

router = APIRouter()


class ActorBase(BaseModel):
    first_name: str
    last_name: str


class ActorCreate(ActorBase):
    pass


class ActorResponse(ActorBase):
    actor_id: int
    last_update: datetime
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


@router.get("/films/{film_id}/actors", response_model=List[ActorResponse])
def get_film_actors(film_id: int, db: Session = Depends(get_db)):
    # Check if the film exists
    film = db.query(Film).filter(Film.film_id == film_id).first()
    if film is None:
        raise HTTPException(status_code=404, detail="Film not found")

    # Query for actors in this film
    actors = db.query(Actor).join(FilmActor).filter(FilmActor.film_id == film_id).all()

    if not actors:
        return []  # Return an empty list if no actors are found

    return actors


@router.post("/actors/", response_model=ActorResponse)
def create_actor(actor: ActorCreate, db: Session = Depends(get_db)):
    db_actor = Actor(**actor.dict(), last_update=datetime.now())
    db.add(db_actor)
    db.commit()
    db.refresh(db_actor)
    return db_actor


@router.get("/actors/", response_model=List[ActorResponse])
def read_actors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    actors = db.query(Actor).offset(skip).limit(limit).all()
    return actors


@router.get("/actors/{actor_id}", response_model=ActorResponse)
def read_actor(actor_id: int, db: Session = Depends(get_db)):
    actor = db.query(Actor).filter(Actor.actor_id == actor_id).first()
    if actor is None:
        raise HTTPException(status_code=404, detail="Actor not found")
    return actor
