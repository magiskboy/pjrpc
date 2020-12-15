import typing as T
import json
import bz2
import os
from dataclasses import asdict
from . import types
from . import errors
from . import utils
from . import spec


compress = bz2.compress
decompress = bz2.decompress


def serializer(data: dict) -> bytes:
    string = json.dumps(data, separators=(',', ':'))
    return string.encode('utf-8')


def deserializer(data: bytes) -> dict:
    string = data.decode('utf-8')
    return json.loads(string)


class Stub:
    __slots__ = ('_compress',)

    def __init__(self, compress: bool = False):
        self._compress = compress

    def unpack(self, data: bytes) -> types.Message:
        try:

            if self._compress:
                data_json = deserializer(decompress(data))
            else:
                data_json = deserializer(data)

            message_maker = None
            if spec.is_request(data_json):
                message_maker = utils.make_request_from_data
            else:
                message_maker = utils.make_response_from_data

            if isinstance(data_json, list):
                return [message_maker(**item) for item in data_json]

            return message_maker(**data_json)

        except (json.JSONDecodeError, OSError) as error:
            raise errors.ParseError() from error

    def pack(self, message: T.Union[types.Message]) -> bytes:
        try:

            if isinstance(message, list):
                data = serializer([asdict(item) for item in message])
            else:
                data = serializer(asdict(message))

        except TypeError as error:
            raise errors.ParseError() from error

        if self._compress:
            try:
                return compress(data)
            except OSError as error:
                raise errors.ParseError() from error

        return data
