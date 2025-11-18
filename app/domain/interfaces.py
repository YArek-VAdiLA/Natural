from abc import ABC, abstractmethod
from typing import Optional, Protocol, Any
from io import BytesIO
from .entities import UserEntity, GoalEntity


class AIProvider(Protocol):
    async def ask_goal_assistant(self, user_text: str, current_goal: str | None = None) -> dict: ...

    async def transcribe_voice(self, audio_bytes: BytesIO) -> str:
        ...
    async def chat(self, messages: list, functions: list | None = None) -> Any:
        ...
    async def tts(self, text: str) -> bytes:
        ...

    async def recognize_photo(self, image_bytes: bytes, system_prompt: str) -> str:
        ...

    async def assistant_chat(
        self,
        user_message: str,
        assistant_id: str,
        vector_store_id: str,
        functions: list | None = None
    ) -> Any:
        ...

class UserRepo(ABC):
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: str) -> Optional[UserEntity]:
        ...

    @abstractmethod
    async def create(self, telegram_id: str) -> UserEntity:
        ...

    @abstractmethod
    async def update_goal(self, user_id: int, goal: str) -> None:
        ...

class GoalRepo(ABC):
    @abstractmethod
    async def add_goal(self, user_id: int, goal: str) -> GoalEntity:
        ...
