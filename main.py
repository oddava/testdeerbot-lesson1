import asyncio
from datetime import date
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from dotenv import load_dotenv

from utils.helper_functions import reset_state, rand

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher(storage=MemoryStorage())

class GameState(StatesGroup):
    guessing = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

@dp.message(F.text.regexp(r'\b\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\b'))
async def age_handler(message: Message) -> None:
    birth_date = date.fromisoformat(message.text)
    current_year = date.today()
    age_days = int(abs(current_year - birth_date).days)

    years_old = age_days // 365
    months_old = (age_days - years_old*365)/30

    await message.answer(f"You're {years_old} years {months_old} months old.")

@dp.message(Command("game"))
async def game(message: Message, state: FSMContext) -> None:
    await state.set_state(GameState.guessing)
    await state.update_data(computer_guess=rand(), attempts=8, previous_numbers=[])
    await message.answer("*game started*", parse_mode="markdown")
    await message.answer("Computer chose a number between 1 and 100, can you try to guess it?")

@dp.message(GameState.guessing)
async def handle_game(message: Message, state: FSMContext) -> None:
    try:
        int(message.text)
    except ValueError:
        await message.answer("Please enter a valid number!")
        return

    state_data = await state.get_data()
    if state_data.get("attempts") > 0:
        computer_guess = state_data.get("computer_guess")
        await state.update_data(attempts=state_data.get("attempts")-1)
        await state.update_data(previous_numbers=[*state_data.get("previous_numbers"), int(message.text)])
        if int(message.text) != computer_guess:
            hint = "bigger" if int(message.text) < computer_guess else "smaller"
            attempts = state_data.get("attempts")
            prev_guesses = state_data.get("previous_numbers")
            await message.answer(f"Wrong, try to choose {hint} value.\nAttempts left: {attempts}\nPrevious guesses: {prev_guesses}")
            return
        await message.answer(f"Correct! It was {computer_guess}, thanks for playing.")
        await message.answer("*game ended*", parse_mode="markdown")
        await reset_state(state)
        return
    await message.answer("Oops, you're out of attempts")
    await message.answer("*game ended*", parse_mode="markdown")
    await reset_state(state)

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())