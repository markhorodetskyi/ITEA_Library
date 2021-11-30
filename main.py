from Library.db.sqlite_conn import SqliteConn
# from Library.db.json_conn import JsonConn
from Library.library import Library
from Library.server.routing import on
from Library.server.enums import *
from Library.server import call_result, call
from Library.server.library_handler import SocketHandler
from socket import socket
import threading
from threading import Thread

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
        self.library = Library(choice_db())


    def menu(self, action):
        menu_action = {
            '1': self.add_new_book,
            '2': self.del_book,
            '3': self.edit_book,
            '4': self.add_new_user,
            '5': self.show_books,
            '6': self.show_users,
            '': self.sc.close
        }
        menu_action[action]()

    # @on(Action.GetMenu)
    # def on_get_menu(self, status):
    #     return call_result.GetMenu(
    #         menu_list=LIBRARY.menu()
    #     )

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
            self.library.add_book(author=response.author,
                             title=response.title,
                             genre=response.genre,
                             year=response.year)
            self.give_menu()

    def del_book(self):
        request = call.DelBook(inputs=['Введіть номер книги для ідентифікації: ', ])
        response = self.call(request)
        if response:
            self.library.del_book(target='id', key=response.id)
            self.give_menu()

    def edit_book(self):
        request = call.EditBook(inputs=['Введіть номер книги для ідентифікації: ',
                                          'Введіть полe якe потрібно змінити(title, author, genre, year): ',
                                          'Введіть нове значення: '])
        response = self.call(request)
        if response:
            self.library.edit_book(target='id',
                              key=response.id,
                              update_col=response.update_col,
                              value=response.value)
            self.give_menu()

    def add_new_user(self):
        request = call.AddNewUser(inputs=['Будь ласка введіть ім\'я', 'Будь ласка введіть прізвище'])
        response = self.call(request)
        if response:
            self.library.add_user(name=response.name,
                             surname=response.surname)
            self.give_menu()

    def show_books(self):
        request = call.ShowBook(books=self.library.show_book())
        response = self.call(request)
        if response:
            print(response)
            self.give_menu()

    def show_users(self):
        request = call.ShowUser(users=self.library.show_user())
        response = self.call(request)
        if response:
            print(response)
            self.give_menu()


def start(adr):
    with socket() as server:
        server.bind(adr)
        server.listen(2)
        print(f"[LISTENING] Server is listening on {address[0]}")
        while True:
            conn, addr = server.accept()
            new_client_handler = LibraryHandler(conn)
            server_thread = Thread(target=new_client_handler.run)
            server_thread.start()
            new_client_handler.give_menu()


def choice_db():
    return SqliteConn
    # while True:
    #     print('-------------------------------------')
    #     print('Виберіть тип БД')
    #     print('1. Sql(sql, s)')
    #     print('2. Json(json, j)')
    #     print('Будь ласка введіть номер 1 - 2, або "end(enter)" для завершення програми: ')
    #     choice = input()
    #     if choice in ('1', 'sql', 's'):
    #         return SqliteConn
    #     elif choice in ('2', 'json', 'j'):
    #         return JsonConn
    #     elif choice == 'end' or choice == '':
    #         print('Завершення програми!')
    #         break
    #     else:
    #         print('error')


# def menu():
#     global LIBRARY
#
#     main_loop = True
#     while main_loop:
#         print('-------------------------------------')
#         print('')
#         print('1. Добавити книгу(add, a)')
#         print('2. Видалити книгу(del, d)')
#         print('3. Відредагувати книгу(edit, e)')
#         print('4. Добавити читача(addU, au)')
#         print('5. Показати книги(sb)')
#         print('6. Показати читачів(su)')
#         print('Будь ласка введіть номер 1 - 6, або "end(enter)" для завершення програми: ')
#         task = input()
#         if task in ('1', 'add', 'a'):
#             LIBRARY.add_book(author=input_not_none('Ввведь автора: '),
#                              title=input_not_none('Ввведь назву: '),
#                              genre=input_not_none('Ввведь жанр: '),
#                              year=input_not_none('Ввведь рік: '))
#             LIBRARY.load_from_db()
#         elif task in ('2', 'del', 'd'):
#             LIBRARY.del_book(target='id',
#                              key=input_not_none('Введіть номер книги для ідентифікації: '))
#             LIBRARY.load_from_db()
#         elif task in ('3', 'edit', 'e'):
#             LIBRARY.edit_book(target='id',
#                               key=input_not_none('Введіть номер книги для ідентифікації: '),
#                               update_col=input_not_none('Введіть полe якe потрібно змінити(title, author, genre, year): '),
#                               value=input_not_none('Введіть нове значення: ')
#                               )
#             LIBRARY.load_from_db()
#         elif task in ('4', 'addU', 'au'):
#             LIBRARY.add_user(name=input_not_none('Ввведь ім\'я: '),
#                              surname=input_not_none('Ввведь прізвище: ')
#                              )
#             LIBRARY.load_from_db()
#         elif task in ('5', 'sb'):
#             LIBRARY.show_book()
#         elif task in ('6', 'sr'):
#             LIBRARY.show_user()
#         elif task == 'end' or task == '':
#             print('Завершення програми!')
#             break
#         else:
#             print('error')


if __name__ == '__main__':
    address = ('localhost', 9999)
    start(address)
