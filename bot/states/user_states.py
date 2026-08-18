from aiogram.fsm.state import StatesGroup, State

class SetupStates(StatesGroup):
    waiting_for_city = State()
    schedule_choosing_the_city = State()
    waiting_for_time = State()
    delete_schedule = State()
    weather_by_city = State()