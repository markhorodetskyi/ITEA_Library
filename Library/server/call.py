from typing import List
from dataclasses import dataclass


@dataclass
class GiveMenu:
    menu_list: List


@dataclass
class GetMenu:
    status: bool


@dataclass
class ChoiseMenu:
    msg: str


@dataclass
class AddNewBook:
    inputs: List


@dataclass
class DelBook:
    inputs: List


@dataclass
class EditBook:
    inputs: List


@dataclass
class AddNewUser:
    inputs: List


@dataclass
class ShowBook:
    books: List


@dataclass
class ShowUser:
    users: List
