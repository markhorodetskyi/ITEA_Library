from .connectorDB import Connector
import json
from pathlib import Path
from loguru import logger
from threading import RLock

logger.add(f'Library/log/{__name__}.json',
           format='{time} {level} {message}',
           level='DEBUG',
           rotation='1000 KB',
           compression='zip',
           serialize=True)



class JsonConn(Connector):
    __DB_BOOKS = "Library/db/books_db.json"
    __DB_USERS = "Library/db/users_db.json"
    TYPE = 'json'

    def __init__(self, books_db=None, users_db=None):
        self.__path_books_db = books_db if books_db else self.__DB_BOOKS
        self.__path_users_db = users_db if users_db else self.__DB_USERS
        self.__json_init(self.__path_books_db)
        self.__json_init(self.__path_users_db)
        self.rlock = RLock()

    @staticmethod
    def __json_init(path):
        if not Path(path).is_file():
            open(path, 'w')

    def __db_with_type(self, type_obj):
        return self.__path_books_db if type_obj == 'books' else self.__path_users_db

    def __json_insert(self, type_obj: str, columns):
        path = self.__db_with_type(type_obj)
        with open(path, 'a+') as f:
            f.write(f'{json.dumps(columns)}\n')

    def __json_update(self, type_obj: str, update_col: dict, target_key: dict):
        path = self.__db_with_type(type_obj)
        target = ''.join(key for key in target_key.keys())
        key = ''.join(key for key in target_key.values())
        col = ''.join(key for key in update_col.keys())
        val = ''.join(key for key in update_col.values())
        with open(path, 'r') as fr:
            querry = [json.loads(line) for line in fr]
            for row in range(len(querry)):
                if str(querry[row][target]) == key:
                    querry[row][col] = val
            with open(path, 'w') as fw:
                fw.write(''.join(f'{json.dumps(row)}\n' for row in querry))

    def __json_del(self, type_obj: str, del_key: dict):
        path = self.__db_with_type(type_obj)
        target = ''.join(key for key in del_key.keys())
        key = ''.join(key for key in del_key.values())
        with open(path, 'r') as fr:
            querry = [json.loads(line) for line in fr if str(json.loads(line)[target]) != key]
            with open(path, 'w') as fw:
                fw.write(''.join(f'{json.dumps(row)}\n' for row in querry))

    def read_from_db(self, type_obj, where=None):
        path = self.__db_with_type(type_obj)
        with self.rlock:
            with open(path, 'r') as f:
                if f:
                    querry = [json.loads(line) for line in f]
                    data = [tuple(row.values()) for row in querry]
                    return data
                return ''

    def write_to_db(self, **kwargs):
        with self.rlock:
            if kwargs['action'] == 'INSERT':
                self.__json_insert(kwargs['type_obj'], kwargs['columns'])
            elif kwargs['action'] == 'DELETE':
                self.__json_del(kwargs['type_obj'], kwargs['target'])
            elif kwargs['action'] == 'UPDATE':
                self.__json_update(kwargs['type_obj'], kwargs['update_col'], kwargs['target_key'])
            else:
                print('Неправильний тип операції')
                return False
