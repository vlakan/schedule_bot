from create_bot import bot
from aiogram import types, Dispatcher
from data_base import sqllite_db
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

keyboard = InlineKeyboardMarkup()
button = InlineKeyboardButton('Поделиться 🛸', url='https://t.me/share/url?url=https://t.me/Raspiii_BOT')
keyboard.add(button)


async def get_users(message: types.Message):
    users = await sqllite_db.get_count_users()
    stat = await sqllite_db.get_stat_data()
    await bot.send_message(message.from_user.id, f'Количество пользователей: {users}\n\n'
                                                 f'------Статистика------\n'
                                                 f'Сегодня: {stat[0]}\n'
                                                 f'Завтра: {stat[1]}\n'
                                                 f'Тек неделя: {stat[2]}\n'
                                                 f'След неделя: {stat[3]}\n'
                                                 f'Всего запросов расписания: {stat[0] + stat[1] + stat[2] + stat[3]}')


class dialog(StatesGroup):
    spam = State()


async def spam(message: Message):
    await dialog.spam.set()
    await message.answer('Напиши текст рассылки')


async def start_spam(message: Message, state: FSMContext):
    count = 0
    for user in sqllite_db.get_user_data():
        try:
            count += 1
            await bot.send_message(user[0], message.text)
        except Exception as ex:
            await bot.send_message(chat_id=5119572413, text=f'{ex} {count} {user[0]}')
    await message.answer(f'Рассылка завершена - {count}')
    await state.finish()


async def tell_spam(message: Message):
    count = 0
    for user in sqllite_db.get_user_data():
        try:
            count += 1
            await bot.send_message(user[0], 'Вам понравился бот? Есть способ помочь его развитию...\n'
                                            'Поделитесь с одногруппниками 👇', reply_markup=keyboard)
        except Exception as ex:
            await bot.send_message(chat_id=5119572413, text=f'{ex} {count} {user[0]}')
    await message.answer(f'Рассылка завершена - {count}')


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(get_users, commands=['get_users2310'])
    dp.register_message_handler(tell_spam, text='Рассылкаспам')
    dp.register_message_handler(spam, text='Рассылка2310')
    dp.register_message_handler(start_spam, state=dialog.spam)
