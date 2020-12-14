import json
from dataclasses import asdict
from . import spec
from . import errors


class Stub:
    def pack(self, message: spec.Message) -> bytes:
        pass

    def unpack(self, data: bytes) -> spec.Message:
        pass


class StubServer:
    def pack(self, message: spec.ResponseMessage) -> bytes:
        try:

            data = asdict(message)
            data = json.dumps(message, cls=spec.JSONMessageEncoder, separators=(',', ':')).encode('utf-8')

        except TypeError as error:
            raise errors.MarshallError(str(error)) from error

        else:
            return data

    def unpack(self, data: bytes) -> spec.RequestMessage:
        try:

            data_dict = json.loads(data.decode('utf-8'))
            ret = spec.RequestMessage(**data_dict)

        except json.JSONDecodeError as error:
            raise errors.UnmarshallError() from error

        else:
            return ret


class StubClient:
    def pack(self, message: spec.RequestMessage) -> bytes:
        try:

            data = asdict(message)
            data = json.dumps(message, cls=spec.JSONMessageEncoder).encode('utf-8')

        except TypeError as error:
            raise errors.MarshallError(str(error)) from error

        else:
            return data

    def unpack(self, data: bytes) -> spec.ResponseMessage:
        try:

            data_dict = json.loads(data.decode('utf-8'))
            error = data_dict.pop('error', None)
            ret = spec.ResponseMessage(**data_dict)
            if error:
                ret.error = spec.Error(**error)

        except json.JSONDecodeError as error:
            raise errors.UnmarshallError() from error

        else:
            return ret
