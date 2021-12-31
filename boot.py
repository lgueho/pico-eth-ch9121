import uasyncio as asyncio
from config import SERVER_CONFIG
from server import CH9121

server = CH9121()

loop = asyncio.get_event_loop()
print("start config")
loop.run_until_complete(server.set_tcp_server(**SERVER_CONFIG))
print("config complet")
loop.close()
