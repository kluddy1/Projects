import logging

from aiogram import Dispatcher, Bot, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from movies import movies

load_dotenv()

TOKEN = "6067130720:AAGjD8cDDCiAMXnPnrPjr-wlTaZ-Ls980Zk"
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)

dp = Dispatcher(bot, storage=MemoryStorage())

ADMINS = ['5287842258']

async def set_default_commands():
    await bot.set_my_commands(
        [
            types.BotCommand("start","Start Bot"),
            types.BotCommand("add_movie", "Add new movie")

        ]
    )

@dp.message_handler(commands='start')
async def start(message: types.Message):
    movie_choice = InlineKeyboardMarkup()
    for movie in movies:
        button = InlineKeyboardButton(text=movie, callback_data=movie)
        movie_choice.add(button)
    await message.answer(text="Hi I'm movies Bot!", reply_markup=movie_choice)


@dp.callback_query_handler()
async def get_movie_info(callback_query: types.CallbackQuery):
    if callback_query.data not in movies.keys():
        await bot.send_message(callback_query.message.chat.id, 'No such movie')
    await bot.send_photo(callback_query.message.chat.id, movies[callback_query.data]['photo'])
    desc = movies[callback_query.data]['description']
    #url = movies[callback_query.data]['url']
    message = f"{callback_query.data}\n{desc}\n"
    await bot.send_message(callback_query.message.chat.id, message, parse_mode='html')


movie_name = ""


@dp.message_handler(commands="add_movie")
async def add_movie(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    if user_id in ADMINS:
        await message.answer("Choose movie title")
        await state.set_state("set_movie_name")
    else:
        await message.answer("You do not have perms to do this")


@dp.message_handler(state="set_movie_name")
async def add_movie(message: types.Message, state: FSMContext):
    global movie_name
    if len(message.text) > 64:
        await message.answer(text="too many chars")
    else:
        movie_name = message.text
        movies[movie_name] = {}
        await state.set_state("set_description")
        await message.answer(text="Nice, now describe the movie briefly")


@dp.message_handler(state='set_description')
async def set_description(message: types.Message, state: FSMContext):
    global movie_name
    movie_description = message.text
    movies[movie_name]['description'] = movie_description
    await state.set_state('set_rating')
    await message.answer(text="Perfect, what's the rating of it?")

@dp.message_handler(state='set_rating')
async def set_rating(message: types.Message, state: FSMContext):
    global movie_name
    movie_rating = message.text
    movies[movie_name]['rating'] = movie_rating
    await state.set_state('set_photo')
    await message.answer(text="Now set a photo")


@dp.message_handler(state="set_photo")
async def set_photo(message: types.Message, state: FSMContext):
    global movie_name
    movie_photo = message.text
    movies[movie_name]["photo"] = movie_photo
    await state.finish()
    await message.answer(text="Cool, new movie added")

async def on_startup(dp):
    await set_default_commands(dp)


if __name__ == '__main__':
    executor.start_polling(dp)
