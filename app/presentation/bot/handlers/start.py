from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.presentation.bot.states import GoalStates
from app.application.user_service import UserService
from app.application.goal_service import GoalService


def register_start_handlers(
    router: Router,
    user_service: UserService,
    goal_service: GoalService,
):
    @router.message(Command("start"))
    async def cmd_start(message: types.Message, state: FSMContext):
        await state.clear()
        telegram_id = str(message.from_user.id)

        user = await user_service.get_or_create_user(telegram_id)

        await message.answer(
            "Привет! Я помогу тебе с питанием.\n\n"
            "Напиши, пожалуйста, свою цель (например: 'похудеть', 'набор массы')."
        )

        await state.set_state(GoalStates.waiting_for_goal)

    @router.message(GoalStates.waiting_for_goal)
    async def process_goal(message: types.Message, state: FSMContext):
        goal_text = message.text.strip()

        telegram_id = str(message.from_user.id)
        user = await user_service.get_or_create_user(telegram_id)

        await goal_service.save_goal(user, goal_text)

        await message.answer(f"Отлично! Я записал твою цель: <b>{goal_text}</b> 🎯")

        await state.clear()
