from aiogram import types
from asyncpg import Connection, Record
from asyncpg.exceptions import UniqueViolationError

from load_all import bot, dp, db

class DBCommands:
    pool: Connection = db
    add_new_user = "INSERT INTO users(chat_id, username, full_name) VALUES ($1,$2,$3) RETURNING id"
    add_new_user_referral = "INSERT INTO users(chat_id, username, full_name, referral) VALUES ($1,$2,$3,$4) RETURNING id"
    count_users = "SELECT COUNT(*) from users"
    get_id = "SELECT id FROM users WHERE chat_id = $1"
    check_referrals = "SELECT chat id FROM users WHERE referral = " \
                      "(SELECT id FROM users WHERE chat_id = $1)"
    check_balans = ("SELECT balanse FROM users WHERE chat_id = $1")
    add_money = ("UPDATE users SET balance+$1 WHERE chat_id = $2")

    async def add_new_user(self, referral=None):
        user = types.User.get_current()

        chat_id = user.id
        usermane = user.username
        full_name = user.full_name
        args = (chat_id, usermane, full_name)

        if referral:
            args += (int(referral))
            command = self.add_new_user_referral
        else:
            command = self.add_new_user

        try:
            record_id = await self.pool.fetchval(command, *args)
            return record_id
        except UniqueViolationError:
            pass

    async def count_users(self):
        record: Record = await self.pool.fetchval(self.count_users)
        return record

    async def get_id(self):
        command = self.get_id
        user_id = types.User.get_current().id
        return await self.pool.fetchval(command, user_id)

    async def check_referral(self):
        user_id = types.User.get_current().id
        command = self.check_referrals
        rows = await self.pool.fatch(command, user_id)
        text = ""
        for num, row in enumerate(rows):
            chat = await bot.get_chat(row["chat_id"])
            user_link = chat.get_mention(as_html=True)
            text += str(num + 1) + ". " + user_link
            return  text

    async def check_balance(self):
        command = self.check_balans
        user_id = types.User.get_current()
        return await self.pool.fetchval(command, user_id)

    async def add_money(self, money):
        command = self.add_money
        user_id = types.User.get_current()
        return await self.pool.fetchval(command, money, user_id)

db = DBCommands()

@dp.message_handler(commands=["start"])
async def registrate_user(message: types.Message):
    chat_id = message.from_user.id
    referral = message.get_args()
    id = await db.add_new_user(referral=referral)
    count_users = await db.count_users()

    if not id:
        id = await db.get_id()
    else:
        text = "Новый ID записан в базу данных!"

    bot_username = (await bot.get_me()).username
    id_referral = id
    bot_link = f"https://t.me/{bot_username}?start={id_referral}".format(
        bot_username=bot_username,
        id_referral=id_referral
    )
    balance = await db.check_balance()
    text += f"""
На данный момент в базе дынных {count_users} зарегестрировано

Ваша реферальная ссылка: {bot_link}
Для проверки рефералов введите команду: /referrals

Ваш баланс: {balance} руб.
Чтобы пополнить счет: /add_money 
"""
    await bot.send_message(message, text)