from typing import Optional

from app.domain.entities import GoalDetectionResponse, UserEntity
from app.domain.interfaces import AIProvider
from app.infrastructure.db.repo_impl import SAUserRepo, SAGoalRepo


class GoalService:

    def __init__(self, ai: AIProvider, user_repo: SAUserRepo, goal_repo: SAGoalRepo):
        self.ai = ai
        self.user_repo = user_repo
        self.goal_repo = goal_repo

    async def process_text(self, text: str, user: UserEntity) -> Optional[GoalDetectionResponse]:
        try:
            raw = await self.ai.ask_goal_assistant(text, user.goal)

            if raw is None:
                return None

            return GoalDetectionResponse(
                text = raw.get("text"),
                is_function_call = raw.get("is_function_call", False),
                function_name = raw.get("function_name"),
                function_args = raw.get("function_args"),
            )

        except Exception as e:
            print(f"[GoalService] process_text error: {e}")
            return None

    async def handle_function_call(self, response: GoalDetectionResponse, user: UserEntity) -> bool:
        try:
            if not response.is_function_call:
                return False

            if response.function_name != "save_target":
                return False

            args = response.function_args or {}
            goal = (args.get("goal") or "").strip()

            if not goal:
                return False

            await self.goal_repo.add_goal(user.id, goal)
            await self.user_repo.update_goal(user.id, goal)

            return True

        except Exception as e:
            print(f"[GoalService] handle_function_call error: {e}")
            return False
