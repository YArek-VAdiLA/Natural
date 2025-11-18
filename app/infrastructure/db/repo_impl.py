from typing import Callable, AsyncIterator, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import UserEntity, GoalEntity
from app.domain.interfaces import UserRepo, GoalRepo
from app.infrastructure.db.models import User, Goal
from app.infrastructure.db.database import AsyncSessionLocal


async def default_session_factory() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


class SAUserRepo(UserRepo):
    def __init__(self, session_factory: Callable[[], AsyncIterator[AsyncSession]] = default_session_factory):
        self._session_factory = session_factory

    async def get_by_telegram_id(self, telegram_id: str) -> Optional[UserEntity]:
        async for session in self._session_factory():
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            orm_user: Optional[User] = result.scalar_one_or_none()
            if not orm_user:
                return None
            return UserEntity(
                id=orm_user.id,
                telegram_id=orm_user.telegram_id,
                goal=orm_user.goal,
            )

    async def create(self, telegram_id: str) -> UserEntity:
        async for session in self._session_factory():
            orm_user = User(telegram_id=telegram_id)
            session.add(orm_user)
            await session.commit()
            await session.refresh(orm_user)

            return UserEntity(
                id=orm_user.id,
                telegram_id=orm_user.telegram_id,
                goal=orm_user.goal,
            )

    async def update_goal(self, user_id: int, goal: str) -> None:
        async for session in self._session_factory():
            orm_user: User | None = await session.get(User, user_id)
            if orm_user is None:
                return
            orm_user.goal = goal
            await session.commit()


class SAGoalRepo(GoalRepo):
    def __init__(self, session_factory: Callable[[], AsyncIterator[AsyncSession]] = default_session_factory):
        self._session_factory = session_factory

    async def add_goal(self, user_id: int, goal: str) -> GoalEntity:
        async for session in self._session_factory():
            orm_goal = Goal(user_id=user_id, goal_description=goal)
            session.add(orm_goal)
            await session.commit()
            await session.refresh(orm_goal)

            return GoalEntity(
                id=orm_goal.id,
                user_id=orm_goal.user_id,
                goal_description=orm_goal.goal_description,
                created_at=orm_goal.created_at,
            )

