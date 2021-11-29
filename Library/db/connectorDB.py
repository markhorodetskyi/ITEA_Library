from abc import abstractmethod, ABC


class Connector(ABC):

    @abstractmethod
    def read_from_db(self, **kwargs):
        # print('read from DB')
        pass

    @abstractmethod
    def write_to_db(self, **kwargs):
        # print('write_to_db')
        pass

