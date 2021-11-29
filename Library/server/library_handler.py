from dataclasses import asdict
from queue import Queue, Empty
from loguru import logger
from Library.server.routing import create_route_map
from Library.server import call_result, call
from Library.server.message_utils import send_msg, recv_msg, unpack, default_encoding, MessageType, Call
import json
import uuid
import re
import time
import threading


logger.add(f'Library/log/{__name__}.json',
           format='{time} {level} {message}',
           level='DEBUG',
           rotation='1000 KB',
           compression='zip',
           serialize=True)


def camel_to_snake_case(data):
    """
    https://stackoverflow.com/a/1176023/1073222
    """
    if isinstance(data, dict):
        snake_case_dict = {}
        for key, value in data.items():
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', key)
            key = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

            snake_case_dict[key] = camel_to_snake_case(value)

        return snake_case_dict

    if isinstance(data, list):
        snake_case_list = []
        for value in data:
            snake_case_list.append(camel_to_snake_case(value))

        return snake_case_list

    return data


def remove_nones(dict_to_scan):
    dict_to_scan = {
        k: v for k, v in dict_to_scan.items()
        if v is not None
    }
    return dict_to_scan


def snake_to_camel_case(data):
    """
    https://stackoverflow.com/a/19053800/1073222
    """
    if isinstance(data, dict):
        camel_case_dict = {}
        for key, value in data.items():
            components = key.split('_')
            key = components[0] + ''.join(x.title() for x in components[1:])
            camel_case_dict[key] = snake_to_camel_case(value)

        return camel_case_dict

    if isinstance(data, list):
        camel_case_list = []
        for value in data:
            camel_case_list.append(snake_to_camel_case(value))

        return camel_case_list

    return data


class SocketHandler:
    """
    Класс для опрацювань запитів до сервера або клієнта.
    """

    def __init__(self, sc):
        self.logger = logger
        self._response_timeout = 30
        self.sc = sc
        self.route_map = create_route_map(self)
        self._response_queue = Queue()
        self._unique_id_generator = uuid.uuid4
        return

    def handle(self):
        while True:
            # try:
            self.data = recv_msg(self.sc).decode(default_encoding)
            # self.logger.debug('HANDLE')
            if not self.data:
                break
            # self.logger.debug(f'recive --> {self.data}')
            msg = unpack(self.data)
            if msg.message_type_id == MessageType.Call:
                self._handle_call(msg)
            elif msg.message_type_id in [MessageType.CallResult, MessageType.CallError]:
                self._response_queue.put_nowait(msg)
            # except Exception as e:
            #     logger.error(f"[HANDLE ERROR:]: {e}")
            #     self.sc.close()

    def _handle_call(self, msg):
        try:
            handlers = self.route_map[msg.action]
        except KeyError:
            raise NotImplementedError(f"No handler for '{msg.action}' "
                                      "registered.")
        snake_case_payload = camel_to_snake_case(msg.payload)

        try:
            handler = handlers['_on_action']
        except KeyError:
            raise NotImplementedError(f"No handler for '{msg.action}' "
                                      "registered.")

        try:
            response = handler(**snake_case_payload)
        except Exception as e:
            logger.exception(f"Error while handling request '{msg}'")
            response = msg.create_call_error(e).to_json()
            send_msg(response, self.sc)
            return
        print(response)
        temp_response_payload = asdict(response)
        response_payload = remove_nones(temp_response_payload)
        camel_case_payload = snake_to_camel_case(response_payload)
        response = msg.create_call_result(camel_case_payload).to_json()

        self.send(response)

    def call(self, payload, suppress=True):
        camel_case_payload = snake_to_camel_case(asdict(payload))
        call = Call(
            unique_id=str(self._unique_id_generator()),
            action=payload.__class__.__name__,
            payload=remove_nones(camel_case_payload)
        )
        self.send(call.to_json())
        try:
            response = self._get_specific_response(call.unique_id, self._response_timeout)
        except Empty:
            raise Empty(
                f"Waited {self._response_timeout}s for response on "
                f"{call.to_json()}."
            )

        if response.message_type_id == MessageType.CallError:
            logger.warning(f"Received a CALL Error: {response}'")
            if suppress:
                return
            raise response.to_exception()
        else:
            response.action = call.action

        snake_case_payload = camel_to_snake_case(response.payload)
        cls = getattr(call_result, payload.__class__.__name__)  # noqa
        return cls(**snake_case_payload)

    def _get_specific_response(self, unique_id, timeout):
        wait_until = time.time() + timeout
        try:
            # Wait for response of the Call message.
            response = self._response_queue.get(timeout=timeout)
        except Empty:
            raise

        if response.unique_id == unique_id:
            return response

        logger.error(f'Ignoring response with unknown unique id: {response}')
        timeout_left = wait_until - time.time()

        if timeout_left < 0:
            raise Empty

        return self._get_specific_response(unique_id, timeout_left)

    def send(self, message):
        send_msg(bytes(json.dumps(message), default_encoding), self.sc)
