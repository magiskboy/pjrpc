from functools import lru_cache


class PJRPCException(Exception):
    """Base exception for pjrpc"""

    message: str = ''

    code: int = 0


class MarshallError(PJRPCException):
    code = 1

    message = 'Can not pack'

class UnmarshallError(PJRPCException):
    code = 2

    message = 'Can not unpack'

class MethodNotFoundError(PJRPCException):
    code = 3

    message = 'Method not found'


@lru_cache
def get_error_by_code(code: int):
    from pjrpc import errors

    for name in dir(errors):
        if name.endswith('Error'):
            e = getattr(errors, name)
            if e.code == code:
                return e
    return None
