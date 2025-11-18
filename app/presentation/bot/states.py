from aiogram.fsm.state import StatesGroup, State

class GoalStates(StatesGroup):
    waiting_for_goal = State()
