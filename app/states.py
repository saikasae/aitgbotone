from aiogram.fsm.state import State, StatesGroup


class Text(StatesGroup):
    text = State()
    wait = State()


"""
class Image(StatesGroup):
    image = State()
    wait = State()
"""


class Code(StatesGroup):
    code = State()
    wait = State()


"""
class Vision(StatesGroup):
    vision = State()
    wait = State()
"""


class Mailing(StatesGroup):
    message = State()
