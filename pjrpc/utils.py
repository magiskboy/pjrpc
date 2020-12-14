import asyncio
from functools import partial

def load_app_from_string(app_path: str):
    if ':' not in app_path:
        raise ValueError('App path must include name of application')

    module_name, app_name = app_path.rsplit(':', 1)

    module = __import__(module_name)
    app = getattr(module, app_name)

    if app is None:
        raise ValueError('App not found')

    return app


def to_async(timeout=None):
    def to_async_deco(sync_fn):
        async def decorator(*args, **kwargs):
            loop = asyncio.get_event_loop()

            run_fn = partial(sync_fn, *args, **kwargs)

            f = loop.run_in_executor(None, run_fn)

            return await asyncio.wait_for(f, timeout=timeout)
        return decorator
    return to_async_deco
