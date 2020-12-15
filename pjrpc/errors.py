from functools import lru_cache


class PJRPCException(Exception):
    """Base exception for pjrpc"""

    message: str = 'Internal JSON-RPC error.'

    code: int = 32603


class ParseError(PJRPCException):
    code = 32700

    message = 'An error occurred on the server while parsing the JSON text'


class InvalidRequestError(PJRPCException):
    code = 32600

    message = 'The JSON sent is not a valid Request object'


class MethodNotFoundError(PJRPCException):
    code = 32601

    message = 'The method does not exist / is not available'

class InvalidParamError(PJRPCException):
    code = 32602

    message = 'Invalid method parameter(s)'


@lru_cache
def get_error_by_code(code: int):
    from pjrpc import errors

    for name in dir(errors):
        if name.endswith('Error'):
            e = getattr(errors, name)
            if e.code == code:
                return e
    return None
