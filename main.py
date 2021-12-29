from Library.db.sqlite_conn import SqliteConn
from Library.db.json_conn import JsonConn
from Library.library import Library
from Library.server.routing import on
from Library.server.enums import *
from Library.server import call_result, call
from Library.server.library_handler import SocketHandler
from socket import socket
from queue import Queue
from threading import Thread
import concurrent.futures as cf

from loguru import logger

logger.add(f'Library/log/{__name__}.json',
           format='{time} {level} {message}',
           level='DEBUG',
           rotation='1000 KB',
           compression='zip',
           serialize=True)

LIBRARY = None


class LibraryHandler(SocketHandler):

    def __init__(self, sc):
        super(LibraryHandler, self).__init__(sc)
        self.library = Library(SqliteConn)

    def menu(self, action):
        menu_action = {
            '1': self.show_books,
            '2': self.show_free_books,
            '3': self.show_users,
            '4': self.show_book_user,
            '5': self.add_new_book,
            '6': self.del_book,
            '7': self.edit_book,
            '8': self.add_new_user,
            '9': self.del_user,
            '10': self.give_book,
            '11': self.return_book,
            '': self.sc.close
        }
        menu_action[action]()

    @on(Action.ChoiseMenu)
    def on_choise_menu(self, msg):
        self.menu(str(msg))
        return call_result.ChoiseMenu(
            msg='Ok'
        )

    def give_menu(self):
        request = call.GiveMenu(menu_list=self.library.menu())
        response = self.call(request)
        if response:
            self.menu(str(response.choice))

    def add_new_book(self):
        request = call.AddNewBook(inputs=['Будь ласка введіть назву книги: ',
                                          'Будь ласка введіть автора:',
                                          'Будь ласка введіть жанр:',
                                          'Будь ласка введіть рік публікації:'])
        response = self.call(request)
        if response:
            if not self.library.add_book(author=response.author,
                             title=response.title,
                             genre=response.genre,
                             year=response.year):
                self.raise_error("Помилка при додавані книги!")
            self.give_menu()

    def del_book(self):
        request = call.DelBook(inputs=['Введіть номер книги для ідентифікації: ', ])
        response = self.call(request)
        if response:
            if not self.library.del_book(target='id', key=response.id):
                self.raise_error('Помилка при видалені книги!')
            self.give_menu()

    def edit_book(self):
        request = call.EditBook(inputs=['Введіть номер книги для ідентифікації: ',
                                          'Введіть полe якe потрібно змінити(title, author, genre, year): ',
                                          'Введіть нове значення: '])
        response = self.call(request)
        if response:
            if not self.library.edit_book(target='id',
                              key=response.id,
                              update_col=response.update_col,
                              value=response.value):
                self.raise_error('Помилка при редагуванні книги!')
            self.give_menu()

    def give_book(self):
        request = call.GiveBook(inputs=['Введіть номер книги для ідентифікації: ',
                                          'Введіть номер читача для ідентифікації: '])
        response = self.call(request)
        if response:
            if not self.library.edit_book(target='id',
                              key=response.book_id,
                              update_col='user_id',
                              value=response.user_id):
                self.raise_error('Помилка при видачі книги!')
            self.give_menu()

    def return_book(self):
        request = call.ReturnBook(inputs=['Введіть номер книги для ідентифікації: '])
        response = self.call(request)
        if response:
            if not self.library.edit_book(target='id',
                              key=response.book_id,
                              update_col='user_id',
                              value=None):
                self.raise_error('Помилка при повернені книги!')
            self.give_menu()

    def add_new_user(self):
        request = call.AddNewUser(inputs=['Будь ласка введіть ім\'я', 'Будь ласка введіть прізвище'])
        response = self.call(request)
        if response:
            self.library.add_user(name=response.name,
                             surname=response.surname)
            self.give_menu()

    def del_user(self):
        request = call.DelBook(inputs=['Введіть номер читача для ідентифікації: ', ])
        response = self.call(request)
        if response:
            self.library.del_user(target='id', key=response.id)
            self.give_menu()

    def show_books(self):
        self.library.load_from_db()
        request = call.ShowBook(books=self.library.show_book())
        response = self.call(request)
        if response:
            self.give_menu()

    def show_free_books(self):
        self.library.load_from_db()
        request = call.ShowBook(books=self.library.show_free_book())
        response = self.call(request)
        if response:
            self.give_menu()

    def show_users(self, book_id=None):
        self.library.load_from_db()
        request = call.ShowUser(users=self.library.show_user(book_id))
        response = self.call(request)
        if response:
            self.give_menu()

    def show_book_user(self):
        self.library.load_from_db()
        request = call.ShowBookUser(inputs=['Введіть номер книги для ідентифікації: ', ])
        response = self.call(request)
        if response:
            self.show_users(response.id)
            self.give_menu()

    def raise_error(self, msg):
        request = call.Errors(msg=msg)
        response = self.call(request)
        if response:
            self.give_menu()


def start_listener(conn):
    new_client_handler = LibraryHandler(conn)
    Thread(target=new_client_handler.run).start()
    Thread(target=new_client_handler.give_menu).start()


def start(adr):
    with socket() as server:
        server.bind(adr)
        server.listen(3)
        print(f"[LISTENING] Server is listening on {address[0]}")
        with cf.ThreadPoolExecutor(6) as executer:
            while True:
                conn, _ = server.accept()
                print(_)
                executer.submit(start_listener, conn)


if __name__ == '__main__':
    address = ('localhost', 9999)
    start(address)
