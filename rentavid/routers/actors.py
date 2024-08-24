from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from typing import List
from datetime import datetime

from ..dependencies import get_db
from ..models.actor import Actor

router = APIRouter()


class ActorBase(BaseModel):
    first_name: str
    last_name: str


class ActorCreate(ActorBase):
    pass


class ActorResponse(ActorBase):
    actor_id: int
    last_update: datetime

    class Config:
        orm_mode = True


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
