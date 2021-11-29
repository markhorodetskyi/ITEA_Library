from socket import socket
import json
import decimal
from dataclasses import asdict, is_dataclass
from loguru import logger
from .exceptions import (LibraryError, FormatViolationError, PropertyConstraintViolationError,
                         UnknownCallErrorCodeError, ProtocolError)

logger.add(f'Library/log/{__name__}.json',
           format='{time} {level} {message}',
           level='DEBUG',
           rotation='1000 KB',
           compression='zip',
           serialize=True)

default_header_size = 10
default_pack_size = 5
default_encoding = 'utf-8'


class _DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float("%.1f" % obj)
        return json.JSONEncoder.default(self, obj)


def send_msg(msg: bytes, conn: socket, header_size: int = default_header_size) -> bool:
    msg_size = f'{len(msg):{header_size}}'

    if conn.send(msg_size.encode(default_encoding)) != header_size:
        logger.error(f'''ERROR: can't send size message''')
        return False

    if conn.send(msg) != len(msg):
        logger.error(f'''ERROR: can't send message''')
        return False

    return True


def recv_msg(conn: socket, header_size: int = default_header_size, size_pack: int = default_pack_size):
    data = conn.recv(header_size)
    if not data or len(data) != header_size:
        logger.error(f'''ERROR: can't read size message''')
        return False

    size_msg = int(data.decode(default_encoding))
    msg = b''

    while True:
        if size_msg <= size_pack:
            pack = conn.recv(size_msg)
            if not pack:
                return False

            msg += pack
            break

        pack = conn.recv(size_pack)
        if not pack:
            return False

        size_msg -= size_pack
        msg += pack

    return msg


class MessageType:
    """ Номери - класи ідентифікації повідомлення """
    #: Call identifies a request.
    Call = 2

    #: CallResult identifies a successful response.
    CallResult = 3

    #: CallError identifies an erroneous response.
    CallError = 4


def unpack(msg):
    """
    Розпаковка msg відносно типу
    """
    try:
        msg = json.loads(msg)
        msg = json.loads(msg)
    except json.JSONDecodeError as e:
        raise FormatViolationError(f'Message is not valid JSON: {e}')

    for cls in [Call, CallResult, CallError]:
        try:
            if msg[0] == cls.message_type_id:
                return cls(*msg[1:])
        except IndexError:
            raise ProtocolError("Message doesn\'t contain MessageTypeID")

    raise PropertyConstraintViolationError(f"MessageTypeId '{msg[0]}' isn't "
                                           "valid")


class Call:
    """ Call – це тип повідомлення, яке ініціює послідовність запиту/відповіді.
    Це повідомлення можуть надсилати як сервер, так і клієнти.

        Виклик завжди складається з 4 елементів:

            [<MessageTypeId>, "<UniqueId>", "<Action>", {<Payload>}]
    """
    message_type_id = 2

    def __init__(self, unique_id, action, payload):
        self.unique_id = unique_id
        self.action = action
        self.payload = payload

        if is_dataclass(payload):
            self.payload = asdict(payload)

    def to_json(self):
        return json.dumps([
            self.message_type_id,
            self.unique_id,
            self.action,
            self.payload,
        ],
            # By default json.dumps() adds a white space after every separator.
            # By setting the separator manually that can be avoided.
            separators=(',', ':'),
            cls=_DecimalEncoder
        )

    def create_call_result(self, payload):
        call_result = CallResult(self.unique_id, payload)
        call_result.action = self.action
        return call_result

    def create_call_error(self, exception):
        error_code = "InternalError"
        error_description = "An unexpected error occurred."
        error_details = {}

        if isinstance(exception, LibraryError):
            error_code = exception.code
            error_description = exception.description
            error_details = exception.details

        return CallError(
            self.unique_id,
            error_code,
            error_description,
            error_details,
        )

    def __repr__(self):
        return f"<Call - unique_id={self.unique_id}, action={self.action}, " \
               f"payload={self.payload}>"


class CallResult:
    message_type_id = 3

    def __init__(self, unique_id, payload, action=None):
        self.unique_id = unique_id
        self.payload = payload

        # Strictly speaking no action is required in a CallResult. But in order
        # to validate the message it is needed.
        self.action = action

    def to_json(self):
        return json.dumps([
            self.message_type_id,
            self.unique_id,
            self.payload,
        ],
            # By default json.dumps() adds a white space after every separator.
            # By setting the separator manually that can be avoided.
            separators=(',', ':'),
            cls=_DecimalEncoder
        )

    def __repr__(self):
        return f"<CallResult - unique_id={self.unique_id}, " \
               f"action={self.action}, " \
               f"payload={self.payload}>"


class CallError:
    message_type_id = 4

    def __init__(self, unique_id, error_code, error_description,
                 error_details=None):
        self.unique_id = unique_id
        self.error_code = error_code
        self.error_description = error_description
        self.error_details = error_details

    def to_json(self):
        return json.dumps([
            self.message_type_id,
            self.unique_id,
            self.error_code,
            self.error_description,
            self.error_details,
        ],
            separators=(',', ':'),
            cls=_DecimalEncoder
        )

    def to_exception(self):
        for error in LibraryError.__subclasses__():
            if error.code == self.error_code:
                return error(
                    description=self.error_description,
                    details=self.error_details
                )
        raise UnknownCallErrorCodeError(f'''Error code '{self.error_code}' is not defined''')

    def __repr__(self):
        return f"<CallError - unique_id={self.unique_id}, " \
               f"error_code={self.error_code}, " \
               f"error_description={self.error_description}, " \
               f"error_details={self.error_details}>"
