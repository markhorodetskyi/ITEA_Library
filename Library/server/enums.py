from enum import Enum


class Action(str, Enum):
    GiveMenu = "GiveMenu"
    GetMenu = "GetMenu"
    ChoiseMenu = "ChoiseMenu"
    AddNewBook = "AddNewBook"
    AddNewUser = "AddNewUser"
    DelBook = "DelBook"
    EditBook = "EditBook"
    ShowBook = "ShowBook"
    ShowUser = "ShowUser"