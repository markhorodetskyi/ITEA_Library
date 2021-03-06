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
        return ['1. Показати книги',
                '2. Показати незайняті книги',
                '3. Показати читачів',
                '4. Показати читача книги',
                '5. Добавити книгу',
                '6. Видалити книгу',
                '7. Відредагувати книгу',
                '8. Добавити читача',
                '9. Видалити читача',
                '10. Дати книгу читачеві',
                '11. Прийняти книгу від читача',
                'Будь ласка введіть номер 1 - 11, або "end(enter)" для завершення програми: ']

    def load_from_db(self):
        self.books = [Book(*book) for book in self.db.read_from_db(type_obj='books')]
        self.readers = [User(*user) for user in self.db.read_from_db(type_obj='users')]
        self.get_last_book_id()
        self.get_last_user_id()

    def add_book(self, title, author, genre, year):
        if not year.isnumeric():
            return False
        if self.db.write_to_db(action='INSERT', type_obj='books', columns=Book(
                id=self.last_book_id + 1,
                title=title,
                author=author,
                genre=genre,
                year=year,
                user_id=None).__dict__):
            return True
        return False

    def del_book(self, target, key):
        if not key.isnumeric():
            return False
        if not self.get_book_by_id(key):
            return False
        if self.db.write_to_db(action='DELETE', type_obj='books', target={target: key}):
            return True

    def edit_book(self, update_col, value, target, key):
        if not key.isnumeric() and value.isnumeric():
            return False
        if update_col == 'user_id':
            if value != None:
                if not self.get_reader_by_id(int(value)):
                    return False
            book = self.get_book_by_id(int(key))
            print(book, value)
            if not book:
                return False
            if book.user_id != 'None':
                print(book.user_id)
                return False

        if self.db.write_to_db(action='UPDATE',
                               type_obj='books',
                               update_col={update_col: value},
                               target_key={target: key}):
            return True

    def add_user(self, name, surname):
        if self.db.write_to_db(action='INSERT', type_obj='users', columns=User(id=self.last_user_id + 1,
                                                                               name=name,
                                                                               surname=surname).__dict__):
            return False

    def del_user(self, target, key):
        if not key.isnumeric():
            return False
        if not self.get_reader_by_id(key):
            return False
        if self.db.write_to_db(action='DELETE', type_obj='users', target={target: key}):
            return True

    def get_last_book_id(self):
        self.last_book_id = max([book.id for book in self.books]) if self.books else 0
        return self.last_book_id

    def get_last_user_id(self):
        self.last_user_id = max([reader.id for reader in self.readers]) if self.readers else 0
        return self.last_user_id

    def get_book_by_id(self, id_: int) -> Book:
        for book in self.books:
            if book.id == id_:
                return book
        return False

    def get_book_by_user_id(self, id_: int) -> Book:
        for book in self.books:
            if book.user_id == id_:
                return book
        return False

    def get_reader_by_id(self, id_: int) -> User:
        for reader in self.readers:
            if reader.id == id_:
                return reader
        return False

    def show_book(self):
        book_table = [
            f'''{'№':^4} | {'title':^15} | {'author':^30} | {'genre':^15} | {'year':^4} | {'Reader':^6} | ''',
            f'''{'-' * 92:^92}''',
            ''.join(f'{book} \n' for book in self.books),
            f'''{'-' * 92:^92}'''
        ]
        return book_table

    def show_free_book(self):
        book_table = [
            f'''{'№':^4} | {'title':^15} | {'author':^30} | {'genre':^15} | {'year':^4} | ''',
            f'''{'-' * 92:^92}''',
            ''.join(f'{book} \n' for book in self.books if book.user_id == 'None'),
            f'''{'-' * 92:^92}'''
        ]
        print(book_table)
        return book_table

    def show_user(self, book_id):
        if book_id:
            user_id = None
            for book in self.books:
                print(str(book.id) == book_id)
                if str(book.id) == book_id:
                    user_id = book.user_id
            if user_id:
                user_table = [
                    f'''{'№':^4} | {'name':^15} | {'surname':^15} | ''',
                    f'''{'-' * 43:^43}''',
                    ''.join(f'{user} \n' for user in self.readers if user.id == user_id),
                    f'''{'-' * 43:^43}'''
                ]
                return user_table
            else:
                return False
        user_table = [
            f'''{'№':^4} | {'name':^15} | {'surname':^15} | ''',
            f'''{'-' * 43:^43}''',
            ''.join(f'{user} \n' for user in self.readers),
            f'''{'-' * 43:^43}'''
        ]
        return user_table
