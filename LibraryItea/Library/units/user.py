import json


class User:
    def __init__(self, id, name, surname):
        self.id = id
        self.name = name
        self.surname = surname

    def __str__(self):
        return f'{self.id:^4} | ' \
               f'{self.name:^15} | ' \
               f'{self.surname:^15} | '

    def to_json(self):
        return json.dumps(self.__dict__)

    def show_takes_book(self):
        pass

    def show_read_book(self):
        pass

