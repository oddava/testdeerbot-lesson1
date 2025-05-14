import asyncio
from datetime import date
import logging
import sys
from os import getenv
import random

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.text_decorations import markdown_decoration
from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

rand = lambda: random.randint(1, 100)

class State:
    game: bool = False
    computer_guess: int = None
    attempts: int = 8
    previous_guesses: list = []

def reset_state():
    State.attempts = 8
    State.previous_guesses = []
    State.game = False

dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(F.text.regexp(r'\b\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\b'))
async def age_handler(message: Message) -> None:
    birth_date = date.fromisoformat(message.text)
    current_year = date.today()
    age_days = int(abs(current_year - birth_date).days)

    years_old = age_days // 365
    months_old = (age_days - years_old*365)/30

    await message.answer(f"You're {years_old} years {months_old} months old.")

@dp.message(F.text == "game")
async def game(message: Message) -> None:
    State.game = True
    await message.answer("*game started*", parse_mode="markdown")
    await message.answer("Computer chose a number between 1 and 100, can you try to guess it?")
    State.computer_guess = rand()

@dp.message()
async def handle_game(message: Message) -> None:
    if message.text == "quit":
        await message.answer("Thanks for playing")
        await message.answer("*game ended*", parse_mode="markdown")
        reset_state()
        return
    elif State.game:
        try:
            int(message.text)
        except ValueError:
            await message.answer("Please enter a correct type!")
            return

        if State.attempts > 0:
            computer_guess = State.computer_guess
            State.attempts = State.attempts - 1
            if int(message.text) != computer_guess:
                hint = "bigger" if int(message.text) < computer_guess else "smaller"
                State.previous_guesses.append(int(message.text))
                await message.answer(f"Wrong, try to choose {hint} value.\nAttempts left: {State.attempts}\nPrevious guesses: {State.previous_guesses}")
                return
            await message.answer(f"Correct! It was {computer_guess}, thanks for playing.")
            await message.answer("*game ended*", parse_mode="markdown")
            reset_state()
            return
        await message.answer("Oops, you're out of attempts")
        await message.answer("*game ended*", parse_mode="markdown")
        reset_state()
    await message.send_copy(message.chat.id)

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())