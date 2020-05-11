import ssl

import asyncpg

from modules.logger import log_error


class DataBase:
    def __init__(
            self, isSsl, host, port,
            user, password, database,
            tableIn, tableOut):
        self.isSsl = isSsl
        self.host = host
        self.port = port
        self.user = user
        self.pw = password
        self.db = database
        self.tableIn = tableIn
        self.tableOut = tableOut

    async def start_pool(self):
        if self.isSsl:
            sslContext = ssl.SSLContext()
            sslContext.verify_mode = ssl.CERT_NONE
        else:
            sslContext = False
        self.pool = await asyncpg.create_pool(
            ssl=sslContext, host=self.host, port=self.port,
            user=self.user, password=self.pw, database=self.db)

    async def add_entry(self, name, email, phone, timestamp, listId):
        if not name and not phone:
            query = 'INSERT INTO {} (email, time, list)'
            query += " VALUES ('{}', '{}', '{}')"
            query = query.format(self.tableOut, email, timestamp, listId)
        elif not name:
            query = 'INSERT INTO {} (email, phone, time, list)'
            query += " VALUES ('{}', '{}', '{}', '{}')"
            query = query.format(
                self.tableOut, email, phone, timestamp, listId)
        elif not phone:
            query = 'INSERT INTO {} (name, email, time, list)'
            query += " VALUES ('{}', '{}', '{}', '{}')"
            query = query.format(
                self.tableOut, name, email, timestamp, listId)
        else:
            query = 'INSERT INTO {} (name, email, phone, time, list)'
            query += " VALUES ('{}', '{}', '{}', '{}', '{}')"
            query = query.format(
                self.tableOut, name, email, phone, timestamp, listId)

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
        query = 'SELECT * FROM {} ORDER BY time'.format(self.tableOut)
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
        query = 'DELETE FROM {} WHERE id={}'.format(self.tableOut, id)
        connection = await self.pool.acquire()

        try:
            await connection.execute(query)
        except Exception as e:
            text = 'Не удалось удалить нужную запись базы.'
            text += '\nОшибка: {}\nЗапрос: {}'
            log_error(text.format(str(e), query))
        finally:
            await self.pool.release(connection)

    async def get_day(self, day):
        query = "SELECT * FROM {} WHERE time >= DATE '{}'"
        query += " AND time < DATE '{}' + INTERVAL '1' DAY"
        query = query.format(self.tableOut, day, day)
        connection = await self.pool.acquire()

        try:
            await connection.execute("SET timezone = 'Europe/Moscow'")
            data = await connection.fetch(query)
        except Exception as e:
            text = 'Не удалось получить день из базы.'
            text += '\nОшибка: {}\nЗапрос: {}'
            log_error(text.format(str(e), query))
            raise(e)
        finally:
            await self.pool.release(connection)

        if data:
            records = list()
            for record in data:
                records.append(dict(record.items()))
            return records
        else:
            return None

    async def clear_day(self, day):
        query = "DELETE FROM {} WHERE time >= DATE '{}'"
        query += " AND time < DATE '{}' + INTERVAL '1' DAY"
        query = query.format(self.tableOut, day, day)
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

    async def add_raw_entry(self, name, email, phone):
        query = 'INSERT INTO {} (name, email, phone)'
        query += " VALUES ('{}', '{}', '{}')"
        query = query.format(self.tableIn, name, email, phone)
        connection = await self.pool.acquire()

        try:
            await connection.execute(query)
        except Exception as e:
            text = 'Не удалось добавить запись в подготовительную базу.'
            text += '\nОшибка: {}\nЗапрос: {}'
            log_error(text.format(str(e), query))
            raise(e)
        finally:
            await self.pool.release(connection)

    async def get_raw_data(self):
        query = 'SELECT * FROM {}'.format(self.tableIn)
        connection = await self.pool.acquire()

        try:
            data = await connection.fetch(query)
        except Exception as e:
            text = 'Не удалось получить данные из подготовительной базы.'
            text += '\nОшибка: {}\nЗапрос: {}'
            log_error(text.format(str(e), query))
            raise(e)
        finally:
            await self.pool.release(connection)

        if data:
            records = list()
            for record in data:
                records.append(dict(record.items()))
            return records
        else:
            return None

    async def set_raw_used(self, id):
        query = 'UPDATE {} SET used = true WHERE id = {}'.format(
            self.tableIn, id)
        connection = await self.pool.acquire()

        try:
            await connection.execute(query)
        except Exception as e:
            text = 'Не удалось отметить запись как использованную.'
            text += '\nОшибка: {}\nЗапрос: {}'
            log_error(text.format(str(e), query))
            raise(e)
        finally:
            await self.pool.release(connection)