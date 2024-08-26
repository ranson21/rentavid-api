from sqlalchemy import Column, Integer, String, DateTime

from ..dependencies import Base


class Actor(Base):
    __tablename__ = "actor"
    actor_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    last_update = Column(DateTime)
