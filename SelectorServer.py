import time
import types
import socket
import logging
import selectors
from yaml import load
from FIXMessage import FIXMessage
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)


ip, port = '127.0.0.1', 8500


class SelectorServer(object):

    def __init__(self, selector=None, ip=ip, port=port):
        self.selector = selector if selector is not None else selectors.DefaultSelector()
        self.ip = ip
        self.port = port
        self.lsock = None
        self.csock_list = []
        self.fix_handler = None

    def start(self):
        logger.debug(f"[SelectorServer] Creating new listening socket on ip [{self.ip}]: port [{self.port}]")
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lsock.bind((self.ip, self.port))
        self.lsock.listen()
        self.lsock.setblocking(False)
        self.selector.register(self.lsock, selectors.EVENT_READ, data=None)

        while True:
            events = self.selector.select(timeout=1)
            for key, mask in events:
                if key.data is None:
                    self.handle_non_data_conn(key.fileobj)
                else:
                    self.handle_data_conn(key, mask)

    def handle_non_data_conn(self, sock):
        conn, addr = sock.accept()
        logger.debug(f"[SelectorServer] Accepting new inbound connection from [{addr}]")

        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
        events = selectors.EVENT_READ
        self.selector.register(conn, events, data=data)
        self.csock_list.append(conn)

    def handle_data_conn(self, key, mask):
        sock = key.fileobj
        logger.debug(f"[SelectorServer] New inbound data from established connection [{sock.getpeername()}]")

        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)
            logger.debug(f"[SelectorServer] Receiving data [{recv_data}]")
            if recv_data:
                self.handle_recv_data(recv_data)
            else:
                self.selector.unregister(sock)
                sock.close()

    def handle_recv_data(self, recv_data):
        fix_message = FIXMessage()
        fix_message.load_string(recv_data.decode('utf-8'))


if __name__ == "__main__":
    s = SelectorServer()
    s.start()

