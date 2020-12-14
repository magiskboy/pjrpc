from functools import lru_cache
import inspect
from . import spec
from . import errors
from . import utils


class RPCApplication:
    """Receive request, routing, process and response to server"""

    def _method_predicate(self, meth):
        return inspect.iscoroutinefunction(meth) or callable(meth)

    @lru_cache(maxsize=1024)
    def _get_func(self, f_name: str):
        for name, func in inspect.getmembers(self, self._method_predicate):
            if name == f_name:
                return func

        raise errors.MethodNotFoundError()

    async def __call__(self, request: spec.RequestMessage) -> spec.ResponseMessage:

        target = self._get_func(request.method)
        params = request.params or {}

        if not inspect.iscoroutinefunction(target):
            target = utils.to_async()(target)

        ret = await target(**params)

        return spec.ResponseMessage(
            id=request.id,
            result=ret,
        )
