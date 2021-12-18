from uasyncio import StreamWriter, StreamReader
from machine import UART, Pin


class CH9121:
    """Server using CH9121 chipset"""

    def __init__(self):
        self.uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
        self.cfg = Pin(14, Pin.OUT, Pin.PULL_UP)
        self.rst = Pin(17, Pin.OUT, Pin.PULL_UP)
        self.writer = StreamWriter(self.uart0, {})
        self.reader = StreamReader(self.uart0)
        self.rst.value(1)
        self.cfg.value(1)

    async def serve(self, dispatch, *args, **kargs):
        """Infinit loop to serve the dispatch function.

        Args:
            dispatch (func): Function to read the request and write the response.
        """
        while True:
            await dispatch(self.reader, self.writer)
