from aiogram import Router

from app.application.goal_service import GoalService
from app.application.nutrition_service import NutritionService
from app.application.user_service import UserService
from app.domain.interfaces import AIProvider

from .start import register_start_handlers
from .text import register_text_handlers
from .voice import register_voice_handlers
from .photo import register_photo_handlers
from .fallback import register_fallback_handlers


def register_all_handlers(
    router: Router,
    user_service: UserService,
    goal_service: GoalService,
    nutrition_service: NutritionService,
    ai_provider: AIProvider,
) -> None:
    register_text_handlers(router, nutrition_service, user_service, goal_service)
    register_voice_handlers(router, nutrition_service, user_service, ai_provider, goal_service)
    register_photo_handlers(router, nutrition_service, ai_provider)
    register_fallback_handlers(router)

