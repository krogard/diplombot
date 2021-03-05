import asyncio
import asyncpg
import logging

from config import host, PG_PASS, PG_USER

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


async def create_db():
    create_db_command = open("create_db.sql", "r").read()

    logging.info("Подключение к Базе Данных...")
    conn: asyncpg.Connection = await asyncpg.connect(
        user=PG_USER,
        password=PG_PASS,
        host=host)

    await conn.execute(create_db_command)
    logging.info("Таблица пользователей была создана")
    await conn.close()

async def create_pool():
    return await asyncpg.create_pool(
        user=PG_USER,
        password=PG_PASS,
        host=host)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_db())
