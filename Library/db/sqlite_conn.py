from .connectorDB import Connector
import sqlite3
from loguru import logger

logger.add(f'Library/log/{__name__}.json',
           format='{time} {level} {message}',
           level='DEBUG',
           rotation='1000 KB',
           compression='zip',
           serialize=True)


class SqliteConn(Connector):

    __DB_LOCATION = "library/db/library_db"
    TYPE = 'sqlite'

    def __init__(self, db_location=None):

        if db_location is not None:
            self.__db_connection = sqlite3.connect(db_location)
        else:
            self.__db_connection = sqlite3.connect(self.__DB_LOCATION)

        self.__cur = self.__db_connection.cursor()

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

    def write_to_db(self, **kwargs):
        try:
            if kwargs['action'] == 'INSERT':
                print(kwargs)
                sql_request = self.__sql_insert_msg(kwargs['type_obj'], kwargs['columns'])
            elif kwargs['action'] == 'DELETE':
                sql_request = self.__sql_del_msg(kwargs['type_obj'], kwargs['target'])
            elif kwargs['action'] == 'UPDATE':
                sql_request = self.__sql_update_msg(kwargs['type_obj'], kwargs['update_col'], kwargs['target_key'])
            else:
                print('Неправильний тип операції')
                return False

            logger.debug(sql_request)
            self.__cur.execute(sql_request)
            self.__db_connection.commit()
        except sqlite3.OperationalError as e:
            if 'no such column' in str(e):
                print('Такої колонки не існує')
                return False

    def close(self):
        self.__db_connection.close()

    def __del__(self):
        self.__db_connection.close()


