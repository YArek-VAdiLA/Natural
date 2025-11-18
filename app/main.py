import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from redis.asyncio import Redis

from app.config import settings
from app.infrastructure.ai.openai_impl import OpenAIProvider
from app.infrastructure.db.repo_impl import SAUserRepo, SAGoalRepo
from app.infrastructure.files.docx_loader import load_docx_text

from app.application.user_service import UserService
from app.application.goal_service import GoalService
from app.application.nutrition_service import NutritionService
from app.presentation.bot.handlers import register_all_handlers

logging.basicConfig(level=logging.INFO)


def get_redis_client() -> Redis:
    return Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
    )


def build_nutrition_service(ai_provider: OpenAIProvider) -> NutritionService:

    base_dir = os.path.dirname(__file__)
    doc_path = os.path.join(base_dir, "infrastructure", "data", "nutrition_tips.docx")

    if not os.path.exists(doc_path):
        logging.error(f" Файл с советами не найден: {doc_path}")
        doc_knowledge = ""
    else:
        doc_knowledge = load_docx_text(doc_path)
        if not doc_knowledge.strip():
            logging.error(f" Файл {doc_path} прочитан, но текст пустой.")
        else:
            logging.info(f" Документ загружен. Первые 300 символов:\n{doc_knowledge[:300]}")

    return NutritionService(ai_provider=ai_provider, doc_knowledge=doc_knowledge)


async def main():
    bot = Bot(token=settings.telegram_token)

    redis_client = get_redis_client()
    storage = RedisStorage(
        redis=redis_client,
        key_builder=DefaultKeyBuilder(with_bot_id=True),
    )

    dp = Dispatcher(storage=storage)
    router = Router()

    ai_provider = OpenAIProvider()
    user_repo = SAUserRepo()
    goal_repo = SAGoalRepo()

    user_service = UserService(user_repo)
    goal_service = GoalService(ai_provider, user_repo, goal_repo)
    nutrition_service = build_nutrition_service(ai_provider)

    register_all_handlers(
        router=router,
        user_service=user_service,
        goal_service=goal_service,
        nutrition_service=nutrition_service,
        ai_provider=ai_provider,
    )

    dp.include_router(router)


    await dp.start_polling(bot)



import sys
def excepthook(exc_type, exc, tb):
    import traceback
    traceback.print_exception(exc_type, exc, tb)

sys.excepthook = excepthook


if __name__ == "__main__":
    asyncio.run(main())
