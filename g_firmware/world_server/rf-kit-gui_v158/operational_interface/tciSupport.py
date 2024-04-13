import os
import re
import time
from threading import Thread, Lock
from config import Config

TCI_SPLIT_COUNT = 2

try:
    import websocket as websocket_import
except ImportError:
    websocket_import = None


def is_websockets_installed():
    return websocket_import is not None


def install_websockets():
    os.system("pip3 install websocket_client")
    os.system('sync')
    try:
        import websocket as ws
        global websocket_import
        websocket_import = ws
        return True
    except ImportError:
        return False


TIMEOUT = 1


class SplitThreadSafeValue:
    def __init__(self, length):
        self.lock = Lock()
        self.values = [None] * length
        self.currentPosition = None  # or 0?

    def get(self):
        self.lock.acquire()
        try:
            if self.currentPosition in range(len(self.values)):
                return self.values[self.currentPosition]
            else:
                return None
        finally:
            self.lock.release()

    def set(self, index, value):
        self.lock.acquire()
        try:
            self.values[index] = value
        finally:
            self.lock.release()

    def set_active_position(self, index):
        self.lock.acquire()
        try:
            self.currentPosition = index
        finally:
            self.lock.release()

    def reset(self):
        self.lock.acquire()
        try:
            self.currentPosition = None
            for index in range(len(self.values)):
                self.values[index] = None
        finally:
            self.lock.release()


class TciWebsocketClient(Thread):

    def receive(self):
        websocket_import.setdefaulttimeout(TIMEOUT)
        while not self.do_stop:
            self.ws = websocket_import.WebSocketApp(self.uri, on_message=self.handle_message, on_close=self.handle_close)
            self.ws.run_forever(ping_interval=TIMEOUT, ping_timeout=TIMEOUT/2.0)

    def handle_message(self, websocket_app, message):
        vfo_number, frequency = self.extract_frequency(message)
        if frequency is not None and vfo_number in range(TCI_SPLIT_COUNT) and not self.do_stop:
            self.threadSafeValue.set(vfo_number, frequency)
        else:
            active_vfo = self.extract_current_vfo(message)
            if active_vfo is not None and active_vfo in range(TCI_SPLIT_COUNT) and not self.do_stop:
                self.threadSafeValue.set_active_position(active_vfo)

    def handle_close(self, websocket_app, close_status_code, close_message):
        self.threadSafeValue.reset()

    def __init__(self, tci_host, tci_port, thread_safe_value):
        super().__init__(target=self.receive)
        super().setDaemon(True)
        self.do_stop = False
        self.uri = None
        if tci_host is not None and tci_port is not None:
            self.uri = "ws://" + tci_host + ":" + str(tci_port)
        self.ws = None
        self.threadSafeValue = thread_safe_value

    def stop(self):
        self.do_stop = True
        self.ws.close()
        self.ws = None
        while self.is_alive():
            time.sleep(TIMEOUT / 20.0)

    def extract_frequency(self, string):
        p = re.compile('vfo:(\d+),(\d+),(\d+);')
        match = p.match(string)
        if match is not None and match.group(1) == '0':
            vfo_number = match.group(2)
            frequency = match.group(3)
            return int(vfo_number), frequency
        else:
            return None, None

    def extract_current_vfo(self, string):
        first_vfo_value = 'false'
        second_vfo_value = 'true'
        p = re.compile('split_enable:(\d+),(' + first_vfo_value + '|' + second_vfo_value + ');')
        match = p.match(string)
        if match is not None:
            if match.group(1) == '0':
                split_enable = match.group(2)
                if split_enable == first_vfo_value:
                    return 0
                elif split_enable == second_vfo_value:
                    return 1
        else:
            return None


class TciInterface:
    def __init__(self, operational_interface_control):
        self.operationalInterfaceControl = operational_interface_control
        self.threadSafeValue = SplitThreadSafeValue(TCI_SPLIT_COUNT)
        self.port = Config.get_instance().tciConfig.get("port")
        self.host = Config.get_instance().tciConfig.get("host")
        self.thread = self.create_tci_client()
        self.is_open = False

    def set_host(self, host):
        self.host = host

    def set_port(self, port):
        self.port = port

    def apply(self):
        was_open = self.is_open
        if was_open:
            self.stop_client()
        self.thread = self.create_tci_client()
        if was_open:
            self.start_client()

    def create_tci_client(self):
        return TciWebsocketClient(self.host, self.port, self.threadSafeValue)

    def get_frequency(self):
        return self.threadSafeValue.get()

    def reset_frequency(self):
        self.threadSafeValue.reset()

    def start_client(self):
        self.is_open = True
        if self.thread is None:
            self.thread = self.create_tci_client()
        self.thread.start()

    def stop_client(self):
        self.is_open = False
        if self.thread is not None and self.thread.is_alive():
            self.thread.stop()
        self.thread = None

    def is_configured(self):
        return is_websockets_installed() and self.host is not None and len(self.host) > 0 and self.port is not None
