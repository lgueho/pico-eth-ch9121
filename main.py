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
    token=WEB_CONFIG["token"]
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
