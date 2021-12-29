from typing import List
from dataclasses import dataclass


@dataclass
class GiveMenu:
    choice: str


@dataclass
class GetMenu:
    menu_list: List


@dataclass
class ChoiseMenu:
    msg: str


@dataclass
class AddNewBook:
    title: str
    author: str
    genre: str
    year: str


@dataclass
class DelBook:
    id: int


@dataclass
class EditBook:
    key: int
    update_col: str
    value: str


@dataclass
class GiveBook:
    book_id: str
    user_id: str


@dataclass
class ReturnBook:
    book_id: str


@dataclass
class AddNewUser:
    name: str
    surname: str

@dataclass
class DelUser:
    id: int


@dataclass
class ShowBook:
    msg: str


@dataclass
class ShowUser:
    msg: str

@dataclass
class ShowBookUser:
    id: int

@dataclass
class Errors:
    msg: str