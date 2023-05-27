import json
import calendar

from create_bot import bot
from keyboards import get_faculties, get_courses, get_groups, kb_student_reg, kb_change_profile, kb_onchange_profile, \
    kb_change_week, kb_days
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from data_base import sqllite_db
from parity_check import parity_checker
from datetime import datetime
from datetime import timedelta
from aiogram.utils.exceptions import MessageNotModified


async def for_day(callback: types.CallbackQuery, searchday=None, id=None):
    if callback.data == 'Сегодня':
        await sqllite_db.plus_today()
    if searchday is None:
        searchday = datetime.now()
    if id:
        call_to_sql = await sqllite_db.sql_profile_by_id(id)
        id_message = id
    else:
        call_to_sql = await sqllite_db.sql_profile_by_id(callback.from_user.id)
        id_message = callback.from_user.id
    wday = calendar.weekday(searchday.year, searchday.month, searchday.day)
    day = calendar.day_name[wday]

    with open('my.json', 'r') as file:
        data_set = json.load(file)
        try:
            weekdays = {
                'Monday': 'Понедельник',
                'Tuesday': 'Вторник',
                'Wednesday': 'Среда',
                'Thursday': 'Четверг',
                'Friday': 'Пятница',
                'Saturday': 'Суббота',
                'Sunday': 'Воскресенье'
            }
            day_data = data_set['facultys'][call_to_sql[0]]['courses'][call_to_sql[1]]['groups'][call_to_sql[2]] \
                ['timetable'][parity_checker(date=searchday)][weekdays[day]]
            messages = []
            for lesson in day_data:
                form = lesson.get('Формат занятия')

                if lesson.get('Подгруппа') != 'все':
                    subgroup = f"👥 {lesson.get('Подгруппа')}"
                    if subgroup.endswith(', '):
                        subgroup = f"{subgroup[:-2]}"
                else:
                    subgroup = ''
                prepod = lesson.get('Преподаватель')
                if prepod.endswith(', '):
                    prepod = f"{prepod[:-2]}"

                messages.append((f"🕓 <b>{lesson.get('Время проведения')}</b>  {subgroup}\n"
                                 f"📘 {lesson.get('Дисциплина')} ({form})\n"
                                 f"👤 {prepod}\n"
                                 f"🏢 <b>{lesson.get('Аудитория')}\n</b>"))

            months = {
                1: 'января',
                2: 'февраля',
                3: 'марта',
                4: 'апреля',
                5: 'мая',
                6: 'июня',
                7: 'июля',
                8: 'августа',
                9: 'сентября',
                10: 'октября',
                11: 'ноября',
                12: 'декабря'
            }
            sm = f"📅 <b>{weekdays[day]}, {searchday.day} {months.get(searchday.month)}\n\n</b>" + \
                 '\n'.join(messages)
            if callback.data == '1':
                await callback.answer()
                try:
                    await callback.message.edit_text(sm, reply_markup=kb_student_reg)
                except MessageNotModified:
                    pass
                return
            if callback.data == '2':
                return sm
            await bot.send_message(id_message, f'{sm}', reply_markup=kb_student_reg)
        except KeyError:
            sm = f"<b>{weekdays[day]} - {searchday.day}.{searchday.month}\n\nПар нет!</b>"
            await bot.send_message(id_message, sm, reply_markup=kb_student_reg)


async def for_tomorrow(callback: types.CallbackQuery):
    await callback.answer()
    await sqllite_db.plus_tomorrow()
    searchday = datetime.now() + timedelta(1)
    t = await for_day(callback, searchday=searchday)
    try:
        await callback.message.edit_text(t, reply_markup=kb_student_reg)
    except MessageNotModified:
        pass


async def for_this_week(message: types.Message, today=None, delta=timedelta(1), id_message=None):
    if today is None:
        today = datetime.now()
    calendar_day = calendar.weekday(today.year, today.month, today.day)
    day = calendar.day_name[calendar_day]

    while day != 'Monday':
        today -= delta
        calendar_day = calendar.weekday(today.year, today.month, today.day)
        day = calendar.day_name[calendar_day]

    for _ in range(6):
        await for_day(message, searchday=today, id=id_message)
        today += timedelta(1)


async def for_next_week(message: types.Message, id_message=None):
    today = datetime.now()
    calendar_day = calendar.weekday(today.year, today.month, today.day)
    day = calendar.day_name[calendar_day]

    if day == 'Monday':
        today += timedelta(7)
    await for_this_week(message, today=today, delta=(-timedelta(1)), id_message=id_message)


async def command_my_profile(message: types.Message):
    call_to_sql = await sqllite_db.sql_profile_by_id(message.from_user.id)
    with open('my.json', 'r') as file:
        data = json.load(file)

        faculty = data['facultys'][call_to_sql[0]].get('facname')
        course = data['facultys'][call_to_sql[0]]['courses'][call_to_sql[1]].get('coursename')[0]
        group = data['facultys'][call_to_sql[0]]['courses'][call_to_sql[1]]['groups'][call_to_sql[2]].get('groupname')
        await bot.send_message(message.from_user.id, f'<b>Курс:</b> {course}\n'
                                                     f'<b>Группа:</b> {group}\n'
                                                     f'<b>Факультет:</b> {faculty}'
                               , reply_markup=kb_change_profile)


async def go_back_on_profile(message: types.Message):
    await bot.send_message(message.from_user.id, '<b>Вы вернулись в главное меню</b> ⬅️', reply_markup=kb_student_reg)


class FSMWeeks(StatesGroup):
    parity_of_week = State()
    day = State()


async def week_fsm(message: types.Message):
    await FSMWeeks.parity_of_week.set()
    await bot.send_message(message.from_user.id, '<b>Поиск по неделе</b> 🔎', reply_markup=kb_onchange_profile)
    await bot.send_message(message.from_user.id, 'Выберите неделю', reply_markup=kb_change_week)


async def get_week_parity(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['week'] = callback.data
    if callback.data == '1':
        await sqllite_db.plus_this_week()
    else:
        await sqllite_db.plus_next_week()
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await FSMWeeks.next()
    await bot.send_message(callback.from_user.id, 'Выберите день', reply_markup=kb_days)


async def get_day(callback: types.CallbackQuery, state: FSMContext):
    today = datetime.now()
    if callback.data == 'b':
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        await FSMWeeks.previous()
        await bot.send_message(callback.from_user.id, 'Выберите неделю', reply_markup=kb_change_week)
        return
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    async with state.proxy() as data:
        data['day'] = callback.data

    calendar_day = calendar.weekday(today.year, today.month, today.day)
    day = calendar.day_name[calendar_day]

    if data.get('week') == '1':
        delta = timedelta(1)
        if callback.data == 'A':
            await for_this_week(message=types.Message(), id_message=callback.from_user.id)
            await state.finish()
            return
    else:
        delta = -timedelta(1)
        if callback.data == 'A':
            await for_next_week(message=types.Message(), id_message=callback.from_user.id)
            await state.finish()
            return
        else:
            if day == 'Monday':
                today += timedelta(7)

    while day != 'Monday':
        today -= delta
        calendar_day = calendar.weekday(today.year, today.month, today.day)
        day = calendar.day_name[calendar_day]

    while day != data.get('day'):
        today += timedelta(1)
        calendar_day = calendar.weekday(today.year, today.month, today.day)
        day = calendar.day_name[calendar_day]

    await for_day(message=types.Message(), searchday=today, id=callback.from_user.id)
    await state.finish()


class FSMStudentReg(StatesGroup):
    faculty = State()
    course = State()
    group = State()


async def cm_start(message: types.Message):

    message_id_count = 1
    while True:
        try:
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - message_id_count)
            break
        except Exception as ex:
            print(ex)
            message_id_count += 1
    if message.text == 'Изменить профиль':
        await bot.send_message(message.from_user.id, '<b>Изменение профиля</b> ⚙', reply_markup=kb_onchange_profile)
    await FSMStudentReg.faculty.set()
    await bot.send_message(message.from_user.id, 'Выберите факультет', reply_markup=await get_faculties())


async def load_faculty(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['userid'] = int(callback.from_user.id)
        data['faculty'] = int(callback.data)
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await FSMStudentReg.next()
    await bot.send_message(callback.from_user.id, 'Выберите курс', reply_markup=await get_courses(data['faculty']))


async def load_course(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'f':
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        await FSMStudentReg.previous()
        await bot.send_message(callback.from_user.id, 'Выберите факультет', reply_markup=await get_faculties())
        return
    async with state.proxy() as data:
        data['course'] = int(callback.data)
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await FSMStudentReg.next()
    await bot.send_message(callback.from_user.id, 'Выберите группу', reply_markup=await get_groups(data['faculty'],
                                                                                                   data['course']))


async def load_group(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if callback.data == 'k':
            await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
            await FSMStudentReg.previous()
            await bot.send_message(callback.from_user.id, 'Выберите курс',
                                   reply_markup=await get_courses(data['faculty']))
            return
        else:
            data['group_name'] = int(callback.data)
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await sqllite_db.sql_add_command(state)
    await state.finish()
    await for_day(callback)


async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    message_id_count = 1
    while True:
        try:
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - message_id_count)
            await bot.send_message(message.from_user.id, '<b>Вы вернулись в главное меню</b> ⬅️',
                                   reply_markup=kb_student_reg)
            break
        except Exception as ex:
            print(ex)
            message_id_count += 1


def register_handlers_student(dp: Dispatcher):
    dp.register_message_handler(cm_start, commands=['start'])
    dp.register_callback_query_handler(load_faculty, text=['0', '1', '2', '3', '4', '5', '6', '7'],
                                       state=FSMStudentReg.faculty)
    dp.register_message_handler(cancel_handler, Text(equals='Главное меню', ignore_case=True), state="*")
    dp.register_message_handler(go_back_on_profile, lambda message: 'Назад' in message.text)
    dp.register_callback_query_handler(load_course, text=['f', '0', '1', '2', '3', '4', '5'],
                                       state=FSMStudentReg.course)
    dp.register_callback_query_handler(load_group,
                                       text=['k', '0', '1', '2', '3', '4', '5', '6', '7', '8', '7', '8', '9',
                                             '10', '11', '12', '13', '14', '15', '16'],
                                       state=FSMStudentReg.group)
    dp.register_callback_query_handler(for_day, text=['1'])
    dp.register_callback_query_handler(for_tomorrow, text=['2'])
    dp.register_message_handler(week_fsm, lambda message: 'Неделя' in message.text, state=None)
    dp.register_callback_query_handler(get_week_parity, text=['1', '2'], state=FSMWeeks.parity_of_week)
    dp.register_callback_query_handler(get_day,
                                       text=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'A',
                                             'b'],
                                       state=FSMWeeks.day)
    dp.register_message_handler(command_my_profile, lambda message: 'Мой профиль' in message.text)
    dp.register_message_handler(cm_start, lambda message: 'Изменить профиль' in message.text, state=None)
