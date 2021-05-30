# Либы для работы с телегой
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message, Location
from aiogram.dispatcher import FSMContext

# Другие либы
from utils import *
import sqlite3

#CONST
from config import botToken

# Подключаем базу данных
connect = sqlite3.connect('users.db')
cursor = connect.cursor()

# Инициализируем бота
bot = Bot(token = botToken)
dp = Dispatcher(bot)

# Подсказки комманд
async def set_bot_commands(dp):
    commands = [
        types.BotCommand(command="start", description="Запуск бота"),
        types.BotCommand(command="forecast", description="Отправка прогноза на основе сохраненного местоположения"),
    ]
    await dp.bot.set_my_commands(commands)

# Логика бота
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message, state: FSMContext):
    cursor.execute("""CREATE TABLE IF NOT EXISTS u{}(
        city TEXT
    )""".format(message.from_user.id))
    connect.commit()
    await message.answer('Отправьте свою геолокацию')
    await bot.send_photo(message.from_user.id, photo=open('location.jpg', 'rb'))
    await set_bot_commands(dp)

@dp.message_handler(content_types='location')
async def send_locatione(message: types.Message):
    cursor.execute("INSERT INTO u{} VALUES(?);".format(message.from_user.id), [city_by_coord(message['location']['latitude'], message['location']['longitude'])])
    connect.commit()
    cursor.execute("SELECT * FROM u{}".format(message.from_user.id))
    city = cursor.fetchall()
    await message.answer(predict(city[0][0]))

@dp.message_handler(commands='forecast')
async def send_forecast(message: types.Message):
    cursor.execute("SELECT * FROM u{}".format(message.from_user.id))
    city = cursor.fetchall()
    await message.answer(predict(city[0][0]))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)