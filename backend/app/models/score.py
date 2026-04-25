from sqlalchemy import Column, Integer, String, DateTime, func
from app.core.database import Base


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True, nullable=False)
    user_name = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    game = Column(String, default="snake", nullable=False)
    created_at = Column(DateTime, server_default=func.now())
