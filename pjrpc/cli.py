import os
import click
import asyncio

try:
    import uvloop
except ImportError:
    uvloop = None

from .server import RPCServer
from .utils import load_app_from_string


@click.group()
def cli():
    """Python JSON-RPC framework"""


@cli.command()
@click.argument('app_path')
@click.option('--host', default='localhost', help='Network interface')
@click.option('--port', default=6969, help='Port for listening')
@click.option('--loop', default='auto', type=click.Choice(['auto', 'asyncio', 'uvloop']))
def run(app_path, host, port, loop):
    """Run RPC server from commandline"""

    if loop == 'uvloop':
        if uvloop is None:
            raise RuntimeError('Please install uvloop')
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    elif loop == 'auto' and uvloop:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    app_cls = load_app_from_string(app_path)
    server = RPCServer(host, port, app_cls=app_cls)

    asyncio.run(server.start())
