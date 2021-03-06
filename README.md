## Python JSON-RPC
A lightweight RPC framework for python. It uses JSON-RPC as protocol.

### Features

- Support `async` syntax
- Has commandline tool look like Flask
- Use a directly TCP server, it's faster than using HTTP as transmission media


### How to use?

```python
#example.py

import asyncio
from pjrpc import Service, Client


class PingService:
    async def ping(self, name: str):
        return NotImplemented


class PingServer(PingService, Service):
    async def ping(self, name: str):
        await asyncio.sleep(1)
        return f'Hello {name}'


class PingClient(PingService, Client):
    def ping(self, name: str, **kwargs):
        pass


if __name__ == '__main__':
    async def main():
        client = PingClient()
        async with client:
            ret = await asyncio.gather(
                client.ping(name='David'),
                client.ping(name='John'),
                client.ping(name='Steve'),
            )

            print(ret)

    asyncio.run(main())
```
In the terminal, you can start the server. To start will launch a TCP server and the requests is served by that
```sh
$ pj example:PingServer --compress
```
In another terminal, you can execute client script
```sh
$ python example.py
$ ['Hello David', 'Hello John', 'Hello Steve']
```
