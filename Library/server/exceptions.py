class LibraryError(Exception):
    """ Тут будуть вийнятки
    """
    default_description = ""

    def __init__(self, description=None, details=None):
        self.description = description
        if description is None:
            self.description = self.default_description

        self.details = details
        if self.details is None:
            self.details = {}

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return (self.description, self.details) == \
                (other.description, other.details)

        return NotImplemented

    def __repr__(self):
        return f"<{self.__class__.__name__} - description={self.description},"\
               f" details={self.details}>"

    def __str__(self):
        return f"{self.__class__.__name__}: {self.description},"\
               f" {self.details}"


class ProtocolError(LibraryError):
    code = "ProtocolError"
    default_description = "Payload for Action is incomplete"


class FormatViolationError(LibraryError):
    code = "FormatViolation"
    default_description = "Payload for Action is syntactically incorrect or \
                          structure for Action"


class PropertyConstraintViolationError(LibraryError):
    code = "PropertyConstraintViolation"
    default_description = "Payload is syntactically correct but at least \
                          one field contains an invalid value"


class UnknownCallErrorCodeError(Exception):
    """ Raised when a CALLERROR is received with unknown error code. """
    pass
