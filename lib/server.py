from uasyncio import StreamWriter
from uasyncio import StreamReader
from machine import UART
from machine import Pin
from utime import sleep


class CMD:

    @property
    def server_tcp(self):
        return b'\x57\xab\x10\x00'

    @property
    def save(self):
        return b'\x57\xab\x0d'

    @property
    def exec_conf(self):
        return b'\x57\xab\x0e'

    @property
    def leave(self):
        return b'\x57\xab\x5e'

    def local_ip(self, ip):
        return b'\x57\xab\x11' + bytes(bytearray(ip))

    def subset_mask(self, ip):
        return b'\x57\xab\x12' + bytes(bytearray(ip))

    def gateway(self, ip):
        return b'\x57\xab\x13' + bytes(bytearray(ip))

    def port_1(self, port):
        return b'\x57\xab\x14' + port.to_bytes(2, 'little')

    def baud_rate_1(self, baud_rate=9600):
        return b'\x57\xab\x21' + baud_rate.to_bytes(4, 'little')

    def domaine_name(self, name):
        return b'\x57\xab\x34' + name.encode("utf-8")


class CH9121:
    """Server using CH9121 chipset"""

    def __init__(self):
        self.uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
        self.cfg = Pin(14, Pin.OUT, Pin.PULL_UP)
        self.rst = Pin(17, Pin.OUT, Pin.PULL_UP)
        self.writer = StreamWriter(self.uart0, {})
        self.reader = StreamReader(self.uart0)
        self.rst.value(1)

    async def set_tcp_server(self, ip, port, gateway, mask):
        cmd = CMD()
        commandes = [
            cmd.server_tcp,
            cmd.local_ip(ip),
            cmd.port_1(port),
            cmd.subset_mask(mask),
            cmd.gateway(gateway),
            cmd.baud_rate_1(),
            cmd.save,
            cmd.exec_conf,
            cmd.leave
        ]
        return await self._set_conf(commandes)

    async def _set_conf(self, commandes):
        try:
            self.cfg.value(0)
            for cmd in commandes:
                await self.writer.awrite(cmd)
                sleep(0.1)
        except Exception as ex:
            print(ex)
        finally:
            self.cfg.value(1)

    async def serve(self, dispatch, *args, **kargs):
        """Infinit loop to serve the dispatch function.

        Args:
            dispatch (func): Funct to read the request and write the response.
        """
        self.cfg.value(1)
        while True:
            await dispatch(self.reader, self.writer)
