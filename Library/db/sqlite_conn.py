from .connectorDB import Connector
import sqlite3
from loguru import logger
from threading import RLock
from queue import Queue

logger.add(f'Library/log/{__name__}.json',
           format='{time} {level} {message}',
           level='DEBUG',
           rotation='1000 KB',
           compression='zip',
           serialize=True)


class SqliteConn(Connector):

    __DB_LOCATION = "Library/db/library_db"
    TYPE = 'sqlite'

    def __init__(self, db_location=None):

        if db_location is not None:
            self.__db_connection = sqlite3.connect(db_location, check_same_thread=False)
        else:
            self.__db_connection = sqlite3.connect(self.__DB_LOCATION, check_same_thread=False)

        self.__cur = self.__db_connection.cursor()
        self.create_table()
        self.db_locker = RLock()

    def create_table(self):
        book_table = f'''
            CREATE TABLE IF NOT EXISTS books (
            id integer PRIMARY KEY,
            title text NOT NULL,
            author text NOT NULL,
            genre text NOT NULL,
            year text NOT NULL,
            user_id integer,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        '''
        user_table = f'''
                    CREATE TABLE IF NOT EXISTS users (
                    id integer PRIMARY KEY,
                    name text NOT NULL,
                    surname text NOT NULL
                );
                '''
        self.__cur.execute(book_table)
        self.__cur.execute(user_table)
        self.__db_connection.commit()


    @staticmethod
    def __sql_insert_msg(type_obj: str, columns):
        print(columns)
        column = ', '.join(col for col in columns)
        values = ', '.join(f"'{col}'" for col in columns.values())
        return f'''INSERT INTO {type_obj} ({column}) VALUES ({values});'''

    @staticmethod
    def __sql_update_msg(type_obj: str, update_col: dict, target_key: dict):
        col = ''.join(key for key in update_col.keys())
        val = ''.join(val for val in update_col.values())
        target = ''.join(key for key in target_key.keys())
        key = ''.join(key for key in target_key.values())
        return f'''UPDATE {type_obj} SET {col}='{val}' WHERE {target}='{key}';'''

    @staticmethod
    def __sql_del_msg(type_obj: str, del_key: dict):
        target = ''.join(key for key in del_key.keys())
        key = ''.join(key for key in del_key.values())
        return f'''DELETE from {type_obj} WHERE {target}='{key}';'''

    def read_from_db(self, column='*', type_obj=None, where=None):
        with self.db_locker:
            try:
                if type_obj:
                    if where:
                        where_arg1, where_arg2 = where
                        sql_request = f'SELECT {column} FROM {type_obj} WHERE {where_arg1} = {where_arg2};'
                        return self.__cur.execute(sql_request).fetchall()
                    sql_request = f'SELECT {column} FROM {type_obj};'
                    return self.__cur.execute(sql_request).fetchall()
                else:
                    print('Помилка зчитування даних')
                    return None
            except Exception as e:
                logger.error(e)
                return None

    def write_to_db(self, **kwargs):
        with self.db_locker:
            try:
                if kwargs['action'] == 'INSERT':
                    print(kwargs)
                    sql_request = self.__sql_insert_msg(kwargs['type_obj'], kwargs['columns'])
                    print(sql_request)
                elif kwargs['action'] == 'DELETE':
                    sql_request = self.__sql_del_msg(kwargs['type_obj'], kwargs['target'])
                elif kwargs['action'] == 'UPDATE':
                    sql_request = self.__sql_update_msg(kwargs['type_obj'], kwargs['update_col'], kwargs['target_key'])
                else:
                    print('Неправильний тип операції')
                    return False
                self.__cur.execute(sql_request)
                self.__db_connection.commit()
                logger.debug(sql_request)
                return True

            except sqlite3.OperationalError as e:
                if 'no such column' in str(e):
                    print('Такої колонки не існує')
                    return False

    def close(self):
        self.__db_connection.close()

    def __del__(self):
        self.__db_connection.close()


