from Library.db.sqlite_conn import SqliteConn
from Library.db.json_conn import JsonConn
from Library.library import Library
from loguru import logger


logger.add(f'Library/log/{__name__}.json',
           format='{time} {level} {message}',
           level='DEBUG',
           rotation='1000 KB',
           compression='zip',
           serialize=True)

LIBRARY = None


def choice_db():
    while True:
        print('-------------------------------------')
        print('Виберіть тип БД')
        print('1. Sql(sql, s)')
        print('2. Json(json, j)')
        print('Будь ласка введіть номер 1 - 2, або "end(enter)" для завершення програми: ')
        choice = input()
        if choice in ('1', 'sql', 's'):
            return SqliteConn
        elif choice in ('2', 'json', 'j'):
            return JsonConn
        elif choice == 'end' or choice == '':
            print('Завершення програми!')
            break
        else:
            print('error')


def input_not_none(text: str):
    while True:
        inp = input(text)
        if not inp:
            print('Ви нічого не ввели, спробуйте ще раз!')
            continue
        return inp


def menu():
    global LIBRARY

    main_loop = True
    while main_loop:
        print('-------------------------------------')
        print('')
        print('1. Добавити книгу(add, a)')
        print('2. Видалити книгу(del, d)')
        print('3. Відредагувати книгу(edit, e)')
        print('4. Добавити читача(addU, au)')
        print('5. Показати книги(sb)')
        print('6. Показати читачів(su)')
        print('Будь ласка введіть номер 1 - 3, або "end(enter)" для завершення програми: ')
        task = input()
        if task in ('1', 'add', 'a'):
            LIBRARY.add_book(author=input_not_none('Ввведь автора: '),
                             title=input_not_none('Ввведь назву: '),
                             genre=input_not_none('Ввведь жанр: '),
                             year=input_not_none('Ввведь рік: '))
            LIBRARY.load_from_db()
        elif task in ('2', 'del', 'd'):
            LIBRARY.del_book(target='id',
                             key=input_not_none('Введіть номер книги для ідентифікації: '))
            LIBRARY.load_from_db()
        elif task in ('3', 'edit', 'e'):
            LIBRARY.edit_book(target='id',
                              key=input_not_none('Введіть номер книги для ідентифікації: '),
                              update_col=input_not_none('Введіть полe якe потрібно змінити(title, author, genre, year): '),
                              value=input_not_none('Введіть нове значення: ')
                              )
            LIBRARY.load_from_db()
        elif task in ('4', 'addU', 'au'):
            LIBRARY.add_user(name=input_not_none('Ввведь ім\'я: '),
                             surname=input_not_none('Ввведь прізвище: ')
                             )
            LIBRARY.load_from_db()
        elif task in ('5', 'sb'):
            LIBRARY.show_book()
        elif task in ('6', 'sr'):
            LIBRARY.show_user()
        elif task == 'end' or task == '':
            print('Завершення програми!')
            break
        else:
            print('error')


if __name__ == '__main__':
    LIBRARY = Library(choice_db())
    menu()


