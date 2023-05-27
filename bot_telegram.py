import logging

from aiogram.utils import executor
from create_bot import dp
from handlers import student, admin
from data_base import sqllite_db
import asyncio
import aioschedule
from parse import parse_func


async def scheduler():
    aioschedule.every().day.at("01:27").do(parse_func)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    sqllite_db.sql_start()
    print('Bot is online!')
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    student.register_handlers_student(dp)
    admin.register_handlers_admin(dp)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
# import logging
# import asyncio
# import aioschedule
#
# from create_bot import bot, dp
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
# from aiogram.utils.executor import start_webhook
# from handlers import student, admin
# from data_base import sqllite_db
# from parse import parse_func
#
#
# async def scheduler():
#     aioschedule.every().day.at("04:30").do(parse_func)
#     while True:
#         await aioschedule.run_pending()
#         await asyncio.sleep(1)
#
#
# # webhook settings
# WEBHOOK_HOST = f'https://ea0a-37-145-172-120.eu.ngrok.io'
# WEBHOOK_PATH = f''
# WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'
#
# # webserver settings
# WEBAPP_HOST = '127.0.0.1'
# WEBAPP_PORT = 5000
#
# logging.basicConfig(level=logging.INFO)
# dp.middleware.setup(LoggingMiddleware())
#
#
# async def on_startup(dp):
#     await bot.set_webhook(WEBHOOK_URL)
#     sqllite_db.sql_start()
#     print('Bot is online!')
#     asyncio.create_task(scheduler())
#     # insert code here to run it after start
#
#
# async def on_shutdown(dp):
#     logging.warning('Shutting down..')
#
#     # insert code here to run it before shutdown
#
#     # Remove webhook (not acceptable in some cases)
#     await bot.delete_webhook()
#
#     # Close DB connection (if used)
#     await dp.storage.close()
#     await dp.storage.wait_closed()
#
#     logging.warning('Bye!')
#
#
# if __name__ == '__main__':
#     logging.basicConfig(
#         level=logging.INFO,
#         format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
#     )
#     student.register_handlers_student(dp)
#     admin.register_handlers_admin(dp)
#     start_webhook(
#         dispatcher=dp,
#         webhook_path=WEBHOOK_PATH,
#         on_startup=on_startup,
#         on_shutdown=on_shutdown,
#         skip_updates=True,
#         host=WEBAPP_HOST,
#         port=WEBAPP_PORT,
#     )
