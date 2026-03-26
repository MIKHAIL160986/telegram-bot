print("БОТ ЗАПУСКАЕТСЯ")

import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

TOKEN = "8713922396:AAFl_HrgthIGQacxkXjbgTEo5T6usEtBDNY"
ADMIN_ID = 471578666

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_data = {}

# Главное меню
menu = InlineKeyboardMarkup(row_width=1)
menu.add(
    InlineKeyboardButton("🌴 Подобрать тур", callback_data="tour"),
    InlineKeyboardButton("✍️ Написать менеджеру", callback_data="manager")
)

# Страны
countries = InlineKeyboardMarkup(row_width=2)
countries.add(
    InlineKeyboardButton("Таиланд", callback_data="Таиланд"),
    InlineKeyboardButton("Вьетнам", callback_data="Вьетнам"),
    InlineKeyboardButton("Египет", callback_data="Египет"),
    InlineKeyboardButton("Шри-Ланка", callback_data="Шри-Ланка"),
    InlineKeyboardButton("Абхазия", callback_data="Абхазия"),
    InlineKeyboardButton("Россия", callback_data="Россия"),
    InlineKeyboardButton("Другое", callback_data="Другое")
)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Добро пожаловать в турагентство PEGAS 🌴\nВыберите действие:", reply_markup=menu)

# Нажали "Подобрать тур"
@dp.callback_query_handler(lambda c: c.data == "tour")
async def tour(callback: types.CallbackQuery):
    user_data[callback.from_user.id] = {}
    await bot.send_message(callback.from_user.id, "Выберите страну:", reply_markup=countries)
    user_data[callback.from_user.id]["step"] = "country"

# Нажали "Написать менеджеру"
@dp.callback_query_handler(lambda c: c.data == "manager")
async def manager(callback: types.CallbackQuery):
    await bot.send_message(callback.from_user.id, "Напишите сообщение, и менеджер вам ответит.")
    user_data[callback.from_user.id] = {"step": "chat"}

# Выбор страны
@dp.callback_query_handler(lambda c: c.data in ["Таиланд","Вьетнам","Египет","Шри-Ланка","Абхазия","Россия","Другое"])
async def country(callback: types.CallbackQuery):
    uid = callback.from_user.id
    user_data[uid]["country"] = callback.data
    user_data[uid]["step"] = "people"
    await bot.send_message(uid, "Сколько человек?")

# Обработка сообщений
@dp.message_handler()
async def form(message: types.Message):
    uid = message.from_user.id

    if uid not in user_data:
        return

    step = user_data[uid].get("step")

    if step == "chat":
        await bot.send_message(ADMIN_ID, f"Сообщение от клиента:\n{message.text}")
        await message.answer("Менеджер получил ваше сообщение.")
        return

    if step == "people":
        user_data[uid]["people"] = message.text
        user_data[uid]["step"] = "nights"
        await message.answer("На сколько ночей?")

    elif step == "nights":
        user_data[uid]["nights"] = message.text
        user_data[uid]["step"] = "budget"
        await message.answer("Примерный бюджет?")

    elif step == "budget":
        user_data[uid]["budget"] = message.text
        user_data[uid]["step"] = "phone"
        await message.answer("Оставьте номер телефона")

    elif step == "phone":
        user_data[uid]["phone"] = message.text

        text = f"""
Новая заявка:
Страна: {user_data[uid]['country']}
Людей: {user_data[uid]['people']}
Ночей: {user_data[uid]['nights']}
Бюджет: {user_data[uid]['budget']}
Телефон: {user_data[uid]['phone']}
"""

        await bot.send_message(ADMIN_ID, text)
        await message.answer("Спасибо! Менеджер свяжется с вами.", reply_markup=menu)
        del user_data[uid]

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)