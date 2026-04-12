from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    search = State()
    add = State()
    delete = State()
    useRag = State()