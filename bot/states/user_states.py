from aiogram.fsm.state import StatesGroup, State

class SetupStates(StatesGroup):
    waiting_for_city = State()
    waiting_for_time = State()