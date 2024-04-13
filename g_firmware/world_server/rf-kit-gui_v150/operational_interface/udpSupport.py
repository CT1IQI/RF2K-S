import time
from enum import Enum
from threading import Thread, Lock
import socket
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

from config import Config
from customlogging import log

TIMEOUT = 1


class RadioMode(Enum):
    ACTIVE = ("active radio")
    FIXED = ("radio")

    def __init__(self, displayName):
        self.displayName = displayName

    @classmethod
    def by_display_name(cls):
        return dict([(man.displayName, man) for man in sorted(list(RadioMode), key=lambda m: m.displayName)])


class ThreadSafeValue:
    def __init__(self):
        self.lock = Lock()
        self.value = None
        self.valueTimestamp = time.time_ns()

    def get(self, maxValueAgeInSeconds):
        self.lock.acquire()
        try:
            if time.time_ns() - self.valueTimestamp <= maxValueAgeInSeconds * 1000000000:
                return self.value
            else:
                return None
        finally:
            self.lock.release()

    def set(self, value):
        self.lock.acquire()
        try:
            self.value = value
            self.valueTimestamp = time.time_ns()
        finally:
            self.lock.release()


class UdpServer(Thread):
    def receive(self):
        self.sock.bind(('', self.port))
        while not self.do_stop:
            try:
                received = self.sock.recv(1024)
            except socket.timeout:
                continue
            string = received.decode('utf-8')
            frequency = self.extract_frequency(string)
            if frequency is not None and not self.do_stop:
                self.threadSafeValue.set(frequency)
        self.sock.close()

    def __init__(self, udp_port, thread_safe_value, fixed_radio=None):
        super().__init__(target=self.receive)
        super().setDaemon(True)
        self.do_stop = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT)
        self.port = udp_port
        self.threadSafeValue = thread_safe_value
        self.fixedRadio = fixed_radio

    def stop(self):
        self.do_stop = True
        while self.is_alive():
            time.sleep(TIMEOUT / 20.0)

    def extract_frequency(self, string):
        try:
            tree = ElementTree.fromstring(string)
        except ParseError as e:
            log("could not parse UDP message as XML: " + str(e) + ", message: " + string)
            return None
        transmit_frequencies = tree.findall("./TXFreq")
        radio = tree.findtext("./RadioNr")
        interesting_radio = self.fixedRadio
        if interesting_radio is None:
            interesting_radio = tree.findtext("./ActiveRadioNr")
            if interesting_radio is None:
                interesting_radio = radio
        if len(transmit_frequencies) == 1 and interesting_radio == radio:
            return float(transmit_frequencies[0].text) * 10
        else:
            return None


class UdpInterface:
    def __init__(self, operational_interface_control):
        self.operationalInterfaceControl = operational_interface_control
        self.threadSafeValue = ThreadSafeValue()
        self.port = Config.get_instance().udpConfig["port"]
        configured_radio_mode = RadioMode.by_display_name().get(Config.get_instance().udpConfig.get("radio_mode"))
        self.radioMode = RadioMode.ACTIVE if configured_radio_mode is None else configured_radio_mode
        configured_fixed_radio = Config.get_instance().udpConfig.get("fixed_radio")
        self.fixedRadio = "1" if configured_fixed_radio is None else configured_fixed_radio
        self.thread = self.create_udp_server()
        self.is_open = False

    def get_radio_mode(self):
        return self.radioMode

    def set_radio_mode(self, radio_mode: RadioMode):
        self.radioMode = radio_mode

    def get_fixed_radio(self):
        return self.fixedRadio

    def set_fixed_radio(self, fixed_radio: str):
        self.fixedRadio = fixed_radio

    def set_port(self, port):
        self.port = port

    def apply(self):
        was_open = self.is_open
        if was_open:
            self.stop_server()
        self.thread = self.create_udp_server()
        if was_open:
            self.start_server()

    def create_udp_server(self):
        if self.radioMode is RadioMode.FIXED:
            return UdpServer(self.port, self.threadSafeValue, self.fixedRadio)
        else:
            return UdpServer(self.port, self.threadSafeValue)

    def get_frequency(self):
        return self.threadSafeValue.get(20)

    def reset_frequency(self):
        self.threadSafeValue.set(None)

    def start_server(self):
        self.is_open = True
        if self.thread is None:
            self.thread = self.create_udp_server()
        self.thread.start()

    def stop_server(self):
        self.is_open = False
        if self.thread is not None and self.thread.is_alive():
            self.thread.stop()
        self.thread = None
