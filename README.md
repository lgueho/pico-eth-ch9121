# pico-eth-ch9121

Micropython flask-like for raspberry pi pico and pico-eth-ch9121 Ethernet to UART converter.

## ressources

Pico-eth-ch9121:
- [constructor wiki](https://www.waveshare.com/wiki/Pico-ETH-CH9121).
- [NetModuleConfig.exe](https://h-2technik.com/online/webee/ETH-01/Tool/NetModuleConfig.exe).
- [ETH-01.pdf](https://h-2technik.com/online/webee/ETH-01/H2_ETH-01.pdf)

Raspberry pi pico micropython:
- [firmware](https://micropython.org/download/rp2-pico/).
- [Documentation](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html#technical-specification).

## Lexic

- Pico: Raspberry pi pico Board.
- ch9121: Pico-eth-ch9121 Board.
- Lan: Local Area Network.

## Setup the Pico-eth-ch9121 Board

1. Plug the pico to the ch9121 (follow the usb symbol draw on the ch9121).
1. Plug the usb cable to the pico and the rj45 to the ch9121.
1. To setup the ch9121, use the NetModuleConfig.exe on a computer in the same lan than the ch9121.
1. Follow the configuration describe in the [ETH-01.pdf](https://h-2technik.com/online/webee/ETH-01/H2_ETH-01.pdf)

## project structure

1. `main.py` is the entry point of the code for the pico.
1. `lib` is the default directory for the modules. No need of `__init__.py` file. Our libraries wil be stored their.
1. `lib\server.py` is the class for the ch9121 server with the UART0 configuration.
1. `lib\web.py` is the tiny framework (flask-like) to manage the request and response.
1. `lib\action.py` is only for the exemple.

## exemple

`main.py`

```py
import uasyncio as asyncio
from ujson import dumps, loads
from config import WEB_CONFIG
from server import CH9121
from web import App, reponse
from action import do_led

# Setup the server and the App
server = CH9121()
app = App(
    server=server,
    token=WEB_CONFIG["TOKEN"]
)

# Route section
@app.route('/', methods=["POST"], security=True)
def main(request):
    action = loads(request.headers["action"])
    do_led(action["LED"])
    return reponse(
        http_code=200,
        body=dumps(action),
        content_type="json"
    )

# Loop section
loop = asyncio.get_event_loop()
loop.create_task(app.serve())
loop.run_forever()

```

The very important part is `@app.route('/', methods=["POST"], security=True)`
1. the `route` (here is the root route), Each route must be differente and they are not match pattern.
1. the `methods` allowed (POST, GET...).
1. the `security` (it is optional). The define token in the config.py must be past to the request in the header with the key `token`.
