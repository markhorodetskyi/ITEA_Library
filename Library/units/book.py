import json


class Book:
    def __init__(self, id: int, title: str, author: str, genre: str, year: str, user_id: int = None):
        self.id = id
        self.title = title
        self.author = author
        self.genre = genre
        self.year = year
        self.user_id = user_id

    def __str__(self):
        return f'{self.id:^4} | ' \
               f'{self.title:^15} | ' \
               f'{self.author:^30} | ' \
               f'{self.genre:^15} | ' \
               f'{self.year:^4} | ' \
               f'''{self.user_id if self.user_id else ' ':^6} |'''

    # def __repr__(self):
    #     return json.dumps(self.__dict__)

    def to_json(self):
        return json.dumps(self.__dict__)
