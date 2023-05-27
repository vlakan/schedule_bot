import json
from bs4 import BeautifulSoup
import requests as re
from create_bot import bot
from data_base import sqllite_db


async def parse_func():
    try:
        users = await sqllite_db.get_count_users()
        await bot.send_message(chat_id=5119572413, text=f'Количество пользователей: {users}')
        url = 'https://rsue.ru/raspisanie/'
        req = re.get(url)
        soup = BeautifulSoup(req.text, 'lxml')

        search = soup.find('div', class_='col-lg-6 col-md-6 col-sm-6').find_all('option')

        def parse_schedule(page):
            weekdays_in_nums = {
                'Понедельник': 1,
                'Вторник': 2,
                'Среда': 3,
                'Четверг': 4,
                'Пятница': 5,
                'Суббота': 6
            }

            json_timetable = {}
            weeks = [i.text for i in page.find_all_next('h1', class_='ned')]
            weeks_schedules = page.find_all_next('div', class_='col-lg-2 col-md-2 col-sm-2')
            days = []
            for day in weeks_schedules:
                days.append([i for i in day.get_text().split('\n') if i != ''])
            start_week_index = 0
            for week in weeks:
                json_timetable[week] = {}
                for i in range(start_week_index, len(days)):
                    day = days[i]
                    if day[0] == '\xa0':
                        json_timetable[week][day[0]] = "Сегодня пар нет"
                        continue
                    json_timetable[week][day[0]] = []
                    count = 0
                    for j in range(1, len(day) - 1, 5):
                        lesson_name = day[j + 1]
                        time = day[j][:day[j].find('П')]
                        classroom = day[j + 3][day[j + 3].find('.') + 1:] if day[j + 3].count('д') == 1 else 'Дистанционно'
                        group1 = day[j][day[j].rfind(':') + 2:] if day[j].find('Подгруппа') != -1 else "все"
                        tutor = day[j + 2]
                        if tutor.startswith('-'):
                            tutor = ''
                        lesson_type = day[j + 4]
                        if lesson_type.startswith('Пр'):
                            lesson_type = 'Пр'
                        elif lesson_type.startswith('Ле'):
                            lesson_type = 'Л'
                        else:
                            lesson_type = 'Лаб'

                        # if lesson_name == prev_lesson_name and time == prev_time and classroom == prev_classroom:

                        def search_lessonindex():
                            countless = int
                            for countless, lesson in enumerate(json_timetable[week][day[0]]):
                                if lesson['Дисциплина'] == lesson_name:
                                    break
                            return countless

                        if lesson_name == 'Элективные дисциплины ( модули) по физической культуре и спорту':
                            count += 1
                            if count == 1:
                                json_timetable[week][day[0]].append({
                                    "Время проведения": time,
                                    "Подгруппа": '',
                                    "Дисциплина": lesson_name,
                                    "Преподаватель": '',
                                    "Аудитория": classroom,
                                    "Формат занятия": lesson_type
                                })
                            json_timetable[week][day[0]][search_lessonindex()]['Подгруппа'] += f'{group1}, '
                            json_timetable[week][day[0]][search_lessonindex()]['Преподаватель'] += f'{tutor}, '
                        else:
                            count = 0
                            json_timetable[week][day[0]].append({
                                "Время проведения": time,
                                "Подгруппа": group1,
                                "Дисциплина": lesson_name,
                                "Преподаватель": tutor,
                                "Аудитория": classroom,
                                "Формат занятия": lesson_type
                            })
                    if i < len(days) - 1:
                        next_day = 1
                        while days[i + next_day][0] == '\xa0':
                            next_day += 1
                        if weekdays_in_nums[day[0]] >= weekdays_in_nums[days[i + next_day][0]]:
                            start_week_index = i + 1
                            break
            return json_timetable

        new_dict = {
            'facultys': []
        }

        cc = 0
        for countfac, faculty in enumerate(search[1:]):
            fac = faculty.get('value')
            data = {'query': 'getKinds', 'type_id': fac}
            site = re.post(url=url + 'query.php', data=data)
            new_dict['facultys'].append({'facname': faculty.text, 'courses': []})

            for countcourse, course in enumerate(json.loads(site.text)):
                data = {'query': 'getCategories', 'type_id': fac, 'kind_id': course.get('kind_id')}
                site = re.post(url=url + 'query.php', data=data)
                new_dict['facultys'][countfac]['courses'].append({'coursename': course.get('kind'), 'groups': []})

                for countgroup, group in enumerate(json.loads(site.text)):
                    new_dict['facultys'][countfac]['courses'][countcourse]['groups'].append(
                        {'groupname': group.get('category')})
                    data = {'f': f'{countfac + 1}', 'k': f'{countcourse + 1}', 'g': f'{countgroup + 1}'}
                    cc += 1
                    print(data, cc)
                    response = re.post(url=url, data=data)
                    soup = BeautifulSoup(response.text, 'lxml')
                    content = soup.find('div', id='content').find_all('div', class_='container')[1]
                    timetable = parse_schedule(content)
                    new_dict['facultys'][countfac]['courses'][countcourse]['groups'][countgroup]['timetable'] = timetable

        with open('my.json', 'w') as file:
            file.write(json.dumps(new_dict, indent=4))

        # После парсинга обновляются данные в users_lk.db
        with open('my_copy.json', 'r') as file:
            data_set = json.load(file)
            counter = 0
            for userid, fac, course, group in sqllite_db.get_user_data():
                counter += 1
                data = {}
                user_id = userid
                old_group = data_set['facultys'][fac]['courses'][course]['groups'][group].get('groupname')
                old_course = data_set['facultys'][fac]['courses'][course].get('coursename')
                old_faculty = data_set['facultys'][fac].get('facname')
                print(userid, old_group, old_course, old_faculty)
                with open('my.json', 'r') as file:
                    new_data_set = json.load(file)
                    for countfac, faculty in enumerate(new_data_set['facultys']):
                        if faculty.get('facname') == old_faculty:
                            data['userid'] = user_id
                            data['faculty'] = countfac
                        for countcourse, course in enumerate(new_data_set['facultys'][countfac]['courses']):
                            if course.get('coursename') == old_course:
                                data['course'] = countcourse
                            for countgroup, group in enumerate(
                                    new_data_set['facultys'][countfac]['courses'][countcourse]['groups']):
                                if group.get('groupname') == old_group:
                                    data['groupname'] = countgroup
                                    print(data, counter)
                                    sqllite_db.sql_add_command2(data=data)

        # Запись нового json в json_copy
        with open('my.json', 'r') as file:
            data_set = json.load(file)
            with open('my_copy.json', 'w') as file:
                file.write(json.dumps(data_set, indent=4))

        await bot.send_message(chat_id=5119572413, text=f'Парсинг выполнен успешно! групп - {cc}\n'
                                                        f'Перезаписано юзеров - {counter}')
    except Exception as ex:
        await bot.send_message(chat_id=5119572413, text=f'Парсинг выполнен НЕ успешно!!!\n'
                                                        f'Ошибка - {ex}\n')