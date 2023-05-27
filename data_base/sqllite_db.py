import sqlite3 as sq
from create_bot import bot
from keyboards import kb_student_reg

base = sq.connect('users_lk.db')
cur = base.cursor()
cur.execute("PRAGMA journal_mode=WAL")

base_stat = sq.connect('stat.db')
cur_stat = base_stat.cursor()
cur_stat.execute("PRAGMA journal_mode=WAL")


def sql_start():
    if base:
        print('Data base connected OK!')
    base.execute("""CREATE TABLE IF NOT EXISTS users(
    userid INT PRIMARY KEY,
    faculty INT,
    course INT,
    groupname INT);""")
    base.commit()
    if base_stat:
        print('Data base stat connected OK!')
    base_stat.execute("""CREATE TABLE IF NOT EXISTS stats(
    today INT,
    tomorrow INT,
    week INT,
    next_week INT);""")
    base_stat.commit()


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?)', tuple(data.values()))
        base.commit()


async def sql_checker_id(id):
    if cur.execute(f'SELECT EXISTS(SELECT userid FROM users WHERE userid = {id})'):
        await bot.send_message(id, 'Вы успешно зарегистрированы!', reply_markup=kb_student_reg)


async def sql_profile_by_id(id):
    for i in cur.execute(f'SELECT * from users WHERE userid = {id}').fetchall():
        return i[1], i[2], i[3]


def get_user_data():
    cur.execute('SELECT * from users')
    for row in cur.fetchall():
        if row[0]:
            yield row[0], row[1], row[2], row[3]


def sql_add_command2(data):
    cur.execute(
        f"REPLACE INTO users VALUES ({data.get('userid')}, {data.get('faculty')}, {data.get('course')}, {data.get('groupname')})")
    base.commit()


async def get_count_users():
    cur.execute('SELECT userid from users')
    count = 0
    for row in cur:
        if row[0]:
            count += 1
    return count


async def plus_today():
    cur_stat.execute('UPDATE stats SET today = today + 1')
    base_stat.commit()


async def plus_tomorrow():
    cur_stat.execute('UPDATE stats SET tomorrow = tomorrow + 1')
    base_stat.commit()


async def plus_this_week():
    cur_stat.execute('UPDATE stats SET week = week + 1')
    base_stat.commit()


async def plus_next_week():
    cur_stat.execute('UPDATE stats SET next_week = next_week + 1')
    base_stat.commit()


async def get_stat_data():
    cur_stat.execute('SELECT * from stats')
    for row in cur_stat.fetchall():
        if row[0]:
            return row[0], row[1], row[2], row[3]
