import os
import click
import asyncio

try:
    import uvloop
except ImportError:
    uvloop = None

from . import Server
from . import logging


@click.group()
def cli():
    """Python JSON-RPC framework"""


@cli.command()
@click.argument('app_path')
@click.option('--host', default='localhost', help='Network interface')
@click.option('--port', default=6969, help='Port for listening')
@click.option('--loop', default='auto', type=click.Choice(['auto', 'asyncio', 'uvloop']))
@click.option('--compress', is_flag=True, help='Choice data compression or not')
@click.option('--log-level', type=click.Choice(['error', 'warning', 'debug', 'info']))
def run(app_path, host, port, loop, compress, log_level):
    """Run RPC server from commandline"""

    if loop == 'uvloop':
        if uvloop is None:
            raise RuntimeError('Please install uvloop')
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    elif loop == 'auto' and uvloop:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    logging.set_level(log_level)

    server = Server(app_path, host, port, compress=compress)

    loop = asyncio.get_event_loop()
    loop.create_task(server.start())
    loop.run_forever()
