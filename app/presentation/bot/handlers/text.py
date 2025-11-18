from aiogram import Router, F
from aiogram.types import Message

from app.application.user_service import UserService
from app.application.goal_service import GoalService
from app.application.nutrition_service import NutritionService


def register_text_handlers(
    router: Router,
    nutrition_service: NutritionService,
    user_service: UserService,
    goal_service: GoalService,
):
    @router.message(F.text)
    async def text_handler(message: Message):
        try:
            telegram_id = str(message.from_user.id)
            text = (message.text or "").strip()

            if not text:
                await message.answer("Отправь, пожалуйста, текстовый вопрос ")
                return

            user = await user_service.get_or_create_user(telegram_id)

            goal_resp = await goal_service.process_text(text, user)

            if goal_resp and goal_resp.is_function_call:
                ok = await goal_service.handle_function_call(goal_resp, user)
                if ok:
                    await message.answer(" Цель обновлена!")
                else:
                    await message.answer("Не удалось сохранить цель ")
                return

            answer = await nutrition_service.answer_text(text, user)
            await message.answer(answer.text)

        except Exception as e:
            await message.answer(
                f" Ошибка обработки сообщения: {type(e).__name__}: {e}"
            )
