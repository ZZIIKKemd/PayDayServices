import ssl

import asyncpg

from logger import log_error


class DataBase:
    def __init__(self, host, port, user, password, database, table):
        self.host = host
        self.port = port
        self.user = user
        self.pw = password
        self.db = database
        self.table = table

    async def start_pool(self):
        sslContext = ssl.SSLContext()
        sslContext.verify_mode = ssl.CERT_NONE
        self.pool = await asyncpg.create_pool(
            ssl=sslContext, host=self.host, port=self.port,
            user=self.user, password=self.pw, database=self.db)

    async def add_entry(self, email, timestamp):
        query = "INSERT INTO {} (email, time) VALUES ('{}', '{}')".format(
            self.table, email, timestamp)
        connection = await self.pool.acquire()

        try:
            await connection.execute("SET timezone = 'Europe/Moscow'")
            await connection.execute(query)
        except Exception as e:
            text = 'Не удалось добавить запись в базу.'
            text += '\nОшибка: {}\nЗапрос: {}'
            log_error(text.format(str(e), query))
            raise(e)
        finally:
            await self.pool.release(connection)

    async def get_next(self):
        query = 'SELECT * FROM {} ORDER BY time'.format(self.table)
        connection = await self.pool.acquire()

        try:
            await connection.execute("SET timezone = 'Europe/Moscow'")
            data = await connection.fetchrow(query)
        except Exception as e:
            text = 'Не удалось получить первую строку базы.'
            text += '\nОшибка: {}\nЗапрос: {}'
            log_error(text.format(str(e), query))
            raise(e)
        finally:
            await self.pool.release(connection)

        if data:
            return dict(data.items())
        else:
            return None

    async def remove_entry(self, id):
        query = 'DELETE FROM {} WHERE id={}'.format(self.table, id)
        connection = await self.pool.acquire()

        try:
            await connection.execute(query)
        except Exception as e:
            text = 'Не удалось удалить нужную запись базы.'
            text += '\nОшибка: {}\nЗапрос: {}'
            log_error(text.format(str(e), query))
        finally:
            await self.pool.release(connection)

    async def clear_day(self, day):
        query = "DELETE FROM {} WHERE time >= DATE '{}'"
        query += " AND time < DATE '{}' + INTERVAL '1' DAY"
        query = query.format(self.table, day, day)
        connection = await self.pool.acquire()

        try:
            await connection.execute("SET timezone = 'Europe/Moscow'")
            await connection.execute(query)
        except Exception as e:
            text = 'Не удалось очистить день от запросов.'
            text += '\nОшибка: {}\nЗапрос: {}'
            log_error(text.format(str(e), query))
            raise(e)
        finally:
            await self.pool.release(connection)
