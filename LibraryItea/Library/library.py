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
        print(f'''{'-'*92:^92}''')
        return ''.join(f'{book} \n' for book in self.books)

    def load_from_db(self):
        self.books = [Book(*book) for book in self.db.read_from_db(type_obj='books')]
        self.readers = [User(*user) for user in self.db.read_from_db(type_obj='users')]
        self.get_last_book_id()
        self.get_last_user_id()

    def add_book(self, title, author, genre, year):
        self.db.write_to_db(action='INSERT', type_obj='books', columns=Book(
            id=self.last_book_id+1,
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
        self.db.write_to_db(action='INSERT', type_obj='users', columns=User(id=self.last_user_id+1,
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
        print(f'''{'№':^4} | {'title':^15} | {'author':^30} | {'genre':^15} | {'year':^4} | {'Reader':^6} | ''')
        print(f'''{'-' * 92:^92}''')
        print(''.join(f'{book} \n' for book in self.books))
        print(f'''{'-' * 92:^92}''')
        print()

    def show_user(self):
        print(f'''{'№':^4} | {'name':^15} | {'surname':^15} | ''')
        print(f'''{'-' * 43:^43}''')
        print(''.join(f'{user} \n' for user in self.readers))
        print(f'''{'-' * 43:^43}''')
        print()
