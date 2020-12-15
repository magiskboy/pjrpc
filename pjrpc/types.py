import typing as T
from . import spec

Message = spec.Message

Response = spec.ResponseMessage

ListResponse = T.List[Response]

Request = spec.RequestMessage

ListRequest = T.List[Request]
