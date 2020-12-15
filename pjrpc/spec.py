import typing as T
from json import JSONEncoder
from dataclasses import dataclass


@dataclass
class Error:
    code: str

    message: str

    data: T.Optional[dict] = None


@dataclass
class Message:
    jsonrpc: str = '2.0'


@dataclass
class RequestMessage(Message):
    method: str = None

    params: T.Optional[T.Union[T.Mapping, T.List[T.Mapping]]] = None


@dataclass
class Notification(RequestMessage):
    pass


@dataclass
class CallingMessage(RequestMessage):
    id: T.Union[str, int] = None


@dataclass
class ResponseMessage(Message):
    id: T.Union[str, int] = None


@dataclass
class SuccessResponseMessage(ResponseMessage):
    result: T.Mapping = None


@dataclass
class ErrorResponseMessage(ResponseMessage):
    error: Error = None


def is_request(data_dict: T.Union[list, dict]) -> bool :
    if isinstance(data_dict, list):
        return 'method' in data_dict[0]

    return 'method' in data_dict
