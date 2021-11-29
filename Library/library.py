from .db.sqlite_conn import SqliteConn
from .units.book import Book
from .units.user import User
from loguru import logger

logger.add(f'Library/log/{__name__}.json',
           format='{time} {level} {message}',
           level='DEBUG',
           rotation='1000 KB',
           compression='zip',
           serialize=True)


class Library:
    def __init__(self, db):
        self.books = None
        self.readers = None
        self.db = db()
        self.last_book_id = None
        self.last_user_id = None
        self.load_from_db()

    def __str__(self):
        print(f'''{'№':^4} | {'title':^15} | {'author':^30} | {'genre':^15} | {'year':^4} | {'Reader':^6} | ''')
        print(f'''{'-' * 92:^92}''')
        return ''.join(f'{book} \n' for book in self.books)

    @staticmethod
    def menu():
        return ['1. Добавити книгу(add, a)',
                '2. Видалити книгу(del, d)',
                '3. Відредагувати книгу(edit, e)',
                '4. Добавити читача(addU, au)',
                '5. Показати книги(sb)',
                '6. Показати читачів(su)',
                'Будь ласка введіть номер 1 - 6, або "end(enter)" для завершення програми: ']

    def load_from_db(self):
        self.books = [Book(*book) for book in self.db.read_from_db(type_obj='books')]
        self.readers = [User(*user) for user in self.db.read_from_db(type_obj='users')]
        self.get_last_book_id()
        self.get_last_user_id()

    def add_book(self, title, author, genre, year):
        self.db.write_to_db(action='INSERT', type_obj='books', columns=Book(
            id=self.last_book_id + 1,
            title=title,
            author=author,
            genre=genre,
            year=year,
            user_id=None).__dict__)

    def del_book(self, target, key):
        self.db.write_to_db(action='DELETE', type_obj='books', target={target: key})

    def give_book(self, update_col, value, target, key):
        self.db.write_to_db(action='UPDATE',
                            type_obj='books',
                            update_col={update_col: value},
                            target_key=f"""{target}='{key}'""")

    def edit_book(self, update_col, value, target, key):
        self.db.write_to_db(action='UPDATE',
                            type_obj='books',
                            update_col={update_col: value},
                            target_key={target: key})

    def take_book(self):
        pass

    def add_user(self, name, surname):
        self.db.write_to_db(action='INSERT', type_obj='users', columns=User(id=self.last_user_id + 1,
                                                                            name=name,
                                                                            surname=surname).__dict__)

    def del_user(self, del_key, key):
        self.db.write_to_db(action='DELETE', type_obj='users', del_key=f"""{del_key}='{key}'""")

    def get_last_book_id(self):
        self.last_book_id = max([book.id for book in self.books]) if self.books else 0
        return self.last_book_id

    def get_last_user_id(self):
        self.last_user_id = max([reader.id for reader in self.readers]) if self.readers else 0
        return self.last_user_id

    def show_book(self):
        book_table = [
            f'''{'№':^4} | {'title':^15} | {'author':^30} | {'genre':^15} | {'year':^4} | {'Reader':^6} | ''',
            f'''{'-' * 92:^92}''',
            ''.join(f'{book} \n' for book in self.books),
            f'''{'-' * 92:^92}'''
        ]
        return book_table

    def show_user(self):
        user_table = [
        f'''{'№':^4} | {'name':^15} | {'surname':^15} | ''',
        f'''{'-' * 43:^43}''',
        ''.join(f'{user} \n' for user in self.readers),
        f'''{'-' * 43:^43}'''
        ]
        return user_table
