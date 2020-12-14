import typing as T
from json import JSONEncoder
from dataclasses import dataclass


@dataclass
class Error:
    code: T.Optional[int]

    message: T.Optional[str]


@dataclass
class Message:
    jsonrpc: str = '2.0'

    id: T.Union[str, int] = None


@dataclass
class RequestMessage(Message):
    method: str = None

    params: T.Optional[T.Union[T.Mapping, T.List[T.Mapping]]] = None


@dataclass
class ResponseMessage(Message):
    result: T.Optional[T.Mapping] = None

    error: T.Optional[Error] = None


class JSONMessageEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Message):
            ret = {
                'id': o.id,
                'jsonrpc': o.jsonrpc,
            }

            if isinstance(o, ResponseMessage):
                if o.result:
                    ret['result'] = o.result

                elif error := o.error:
                    ret['error'] = {
                        'code': error.code,
                        'message': error.message,
                    }

            elif isinstance(o, RequestMessage):
                ret['params'] = o.params
                ret['method'] = o.method

            return ret

        return super().default(o)
