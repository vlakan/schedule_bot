import json
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import calendar
from datetime import datetime
from datetime import timedelta

b1 = InlineKeyboardButton('Сегодня', callback_data='1')
b2 = InlineKeyboardButton('Завтра', callback_data='2')
b3 = InlineKeyboardButton('⬇️', callback_data='main')
b4 = InlineKeyboardButton('ℹ Мой профиль', callback_data='4')

kb_student_reg = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb_student_reg.row(b1).row(b2).row(b3)

b5 = KeyboardButton('Назад')
b6 = KeyboardButton('Изменить профиль')

kb_change_profile = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb_change_profile.row(b5, b6)

b7 = KeyboardButton('Главное меню')

kb_onchange_profile = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb_onchange_profile.add(b7)

b8 = InlineKeyboardButton(f'Текущая', callback_data='1')
b9 = InlineKeyboardButton(f'Следующая', callback_data='2')
b10 = InlineKeyboardButton('Назад', callback_data='b')

kb_change_week = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb_change_week.row(b8, b9)

monday = InlineKeyboardButton('Пн', callback_data='Monday')
tuesday = InlineKeyboardButton('Вт', callback_data='Tuesday')
wednesday = InlineKeyboardButton('Ср', callback_data='Wednesday')
thursday = InlineKeyboardButton('Чт', callback_data='Thursday')
friday = InlineKeyboardButton('Пт', callback_data='Friday')
saturday = InlineKeyboardButton('Сб', callback_data='Saturday')

monday2 = InlineKeyboardButton('Пн', callback_data='Monday')
tuesday2 = InlineKeyboardButton('Вт', callback_data='Tuesday')
wednesday2 = InlineKeyboardButton('Ср', callback_data='Wednesday')
thursday2 = InlineKeyboardButton('Чт', callback_data='Thursday')
friday2 = InlineKeyboardButton('Пт', callback_data='Friday')
saturday2 = InlineKeyboardButton('Сб', callback_data='Saturday')


today = datetime.now()
calendar_day = calendar.weekday(today.year, today.month, today.day)
day = calendar.day_name[calendar_day]

while day != 'Monday':
    today -= timedelta(1)
    calendar_day = calendar.weekday(today.year, today.month, today.day)
    day = calendar.day_name[calendar_day]

for _ in range(6):
    today += timedelta(1)
    calendar_day = calendar.weekday(today.year, today.month, today.day)
    day = calendar.day_name[calendar_day]
    print(today)

kb_days = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb_days.row(monday, monday2)


async def get_faculties():
    kb_student_faculty = InlineKeyboardMarkup(row_width=1)
    with open('my.json') as file:
        data = json.load(file)
        for j, i in enumerate(data['facultys']):
            button = InlineKeyboardButton(text=f"{i.get('facname')}", callback_data=f'{j}')
            kb_student_faculty.add(button)
    return kb_student_faculty


async def get_courses(callback1):
    kb_student_course = InlineKeyboardMarkup(row_width=1)
    with open('my.json') as file:
        data = json.load(file)
        for j, i in enumerate(data['facultys'][callback1]['courses']):
            button = InlineKeyboardButton(text=f"{i.get('coursename')}", callback_data=f'{j}')
            kb_student_course.add(button)
    kb_student_course.row(InlineKeyboardButton(text='Назад', callback_data='f'))
    return kb_student_course


async def get_groups(callback1, callback2):
    kb_student_groups = InlineKeyboardMarkup(row_width=1)
    with open('my.json') as file:
        data = json.load(file)
        for j, i in enumerate(data['facultys'][callback1]['courses'][callback2]['groups']):
            button = InlineKeyboardButton(text=f"{i.get('groupname')}", callback_data=f'{j}')
            kb_student_groups.add(button)
    kb_student_groups.row(InlineKeyboardButton(text='Назад', callback_data='k'))
    return kb_student_groups
