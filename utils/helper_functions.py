import random

from aiogram.fsm.context import FSMContext

rand = lambda: random.randint(1, 100)

async def reset_state(state: FSMContext):
    await state.update_data(computer_guess=rand(), attempts=8, previous_numbers=[])
    await state.clear()