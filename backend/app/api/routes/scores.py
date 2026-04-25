from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import List
from app.core.database import get_db
from app.models.score import Score

router = APIRouter()


class ScoreSubmit(BaseModel):
    user_email: str
    user_name: str
    score: int
    game: str = "snake"


class ScoreOut(BaseModel):
    id: int
    user_email: str
    user_name: str
    score: int
    game: str

    class Config:
        from_attributes = True


@router.post("/", response_model=ScoreOut)
async def submit_score(body: ScoreSubmit, db: AsyncSession = Depends(get_db)):
    """提交遊戲分數"""
    new_score = Score(
        user_email=body.user_email,
        user_name=body.user_name,
        score=body.score,
        game=body.game,
    )
    db.add(new_score)
    await db.commit()
    await db.refresh(new_score)
    return new_score


@router.get("/leaderboard", response_model=List[ScoreOut])
async def get_leaderboard(game: str = "snake", limit: int = 10, db: AsyncSession = Depends(get_db)):
    """取得排行榜（每人只取最高分）"""
    # 每個 email 的最高分
    result = await db.execute(
        select(Score)
        .where(Score.game == game)
        .order_by(desc(Score.score))
        .limit(limit * 3)  # 多拿一些再過濾
    )
    all_scores = result.scalars().all()

    # 每人只保留最高分
    seen = {}
    top = []
    for s in all_scores:
        if s.user_email not in seen:
            seen[s.user_email] = True
            top.append(s)
        if len(top) >= limit:
            break

    return top


@router.get("/my-best")
async def my_best_score(user_email: str, game: str = "snake", db: AsyncSession = Depends(get_db)):
    """取得個人最高分"""
    result = await db.execute(
        select(Score)
        .where(Score.user_email == user_email, Score.game == game)
        .order_by(desc(Score.score))
        .limit(1)
    )
    score = result.scalar_one_or_none()
    if not score:
        return {"best_score": 0}
    return {"best_score": score.score}
