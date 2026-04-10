from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    add = State()
    delete = State()