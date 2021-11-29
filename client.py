import socket
from Library.server.routing import on
from Library.server.enums import *
from Library.server import call_result, call
from Library.server.library_handler import SocketHandler


from loguru import logger

logger.add(f'Library/log/{__name__}.json',
           format='{time} {level} {message}',
           level='DEBUG',
           rotation='1000 KB',
           compression='zip',
           serialize=True)


HOST, PORT = "localhost", 9999


def input_to_int(text: str):
    while True:
        try:
            choise = input(text)
            if not choise:
                print('Ви нічого не ввели, спробуйте ще раз!')
                continue
            return int(choise)
        except Exception as e:
            logger.error(e)
            continue


def input_not_none(text: str = ''):
    while True:
        inp = input(text)
        if not inp:
            print('Ви нічого не ввели, спробуйте ще раз!')
            continue
        return inp


class ClientHandler(SocketHandler):

    # def send_get_menu(self):  #Запит до сервера(очікує меню)
    #     request = call.GetMenu(status=True)
    #     response = self.call(request)
    #     print(''.join(f'{i}\n' for i in response.menu_list))
    #     self.send_choise_menu()

    # def send_choise_menu(self):  #Запит до сервера з номером дії(очікує accept)
    #     request = call.ChoiseMenu(msg=input_to_int())
    #     response = self.call(request)
    #     print(response.msg)

    @on(Action.GiveMenu)
    def on_give_menu(self, menu_list):
        print(''.join(f'{i}\n' for i in menu_list))
        return call_result.GiveMenu(choice=input())

    @on(Action.AddNewBook)
    def on_new_book(self, inputs): #Якщо від сервера прийшов запит AddNewBook виконується ця функція. в запиті
                                   # вложена к-сть inputs з повідомлення що потрібно ввести
        title, author, genre, year = [input_not_none(inp) for inp in inputs]
        return call_result.AddNewBook(  # відповідь серверу
            title=title,
            author=author,
            genre=genre,
            year=year
        )

    @on(Action.DelBook)  # те саме що й AddNewBook
    def on_del_book(self, inputs):
        id, = [input_not_none(inp) for inp in inputs]
        return call_result.DelBook(
            id=id
        )

    @on(Action.EditBook)
    def on_edit_book(self, inputs):
        id, update_col, value = [input_not_none(inp) for inp in inputs]
        return call_result.EditBook(
            key=id,
            update_col=update_col,
            value=value
        )

    @on(Action.AddNewUser)
    def on_new_reader(self, inputs):
        name, surname = [input_not_none(inp) for inp in inputs]
        return call_result.AddNewUser(
            name=name,
            surname=surname
        )

    @on(Action.ShowBook)
    def on_show_book(self, books):
        print(''.join(f'{i}\n' for i in books))
        return call_result.ShowBook(
            msg='Ok'
        )

    @on(Action.ShowUser)
    def on_show_user(self, users):
        print(''.join(f'{i}\n' for i in users))
        return call_result.ShowUser(
            msg='Ok'
        )


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cs:
    # cs.connect((HOST, PORT))
    # handler = ClientHandler(cs)
    # handler.handle()
    # # handler_theard.start()
    # # handler.send_get_menu()
    try:
        cs.connect((HOST, PORT))
        handler = ClientHandler(cs)
        handler.handle()
    except Exception as e:
        cs.close()
        logger.error(f"{e}")

