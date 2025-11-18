from app.domain.entities import UserEntity
from app.domain.interfaces import UserRepo


class UserService:
    def __init__(self, user_repo: UserRepo):
        self._user_repo = user_repo

    async def get_or_create_user(self, telegram_id: str) -> UserEntity:
        user = await self._user_repo.get_by_telegram_id(telegram_id)
        if user is not None:
            return user
        return await self._user_repo.create(telegram_id)
