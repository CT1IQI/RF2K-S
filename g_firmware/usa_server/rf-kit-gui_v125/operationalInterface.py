from enum import Enum
from customlogging import log
from tkinter import *

from data import Data
from operational_interface.catSupport import CATInterface
from config import Config

import interface

from operational_interface.tciSupport import TciInterface
from operational_interface.udpSupport import UdpInterface


class OperationalInterface(Enum):
    UNIVERSAL = 0
    CAT = 1
    UDP = 2
    TCI = 3

class OperationalInterfaceControl:

    operationalInterface = None

    @classmethod
    def initOperationalInterface(cls):
        cls.operationalInterface = OperationalInterfaceControl()

    def __init__(self):
        self.currentOperationalInterface = None
        self.selectedOperationalInterface = OperationalInterface[Config.get_instance().operationalInterfaceVar.get()]
        self.currentOperationalInterfaceDisplayName = StringVar()
        self.catInterface = CATInterface(self)
        self.udpInterface = UdpInterface(self)
        self.tciInterface = TciInterface(self)
        self.errorString = ''
        self.errorStringVar = StringVar()
        self.open_operational_interface(self.selectedOperationalInterface)

    def open_operational_interface(self, operational_interface):
        if operational_interface is OperationalInterface.UDP:
            self.open_udp()
        elif operational_interface is OperationalInterface.CAT and self.catInterface.is_configured():
            self.open_cat()
        elif operational_interface is OperationalInterface.TCI and self.tciInterface.is_configured():
            self.open_tci()
        else:
            self.open_univ()
        self.update_operational_interface()

    def close_current_operational_interface(self):
        if self.currentOperationalInterface is OperationalInterface.CAT:
            self.catInterface.close_device()
        elif self.currentOperationalInterface is OperationalInterface.UDP:
            self.udpInterface.stop_server()
        elif self.currentOperationalInterface is OperationalInterface.TCI:
            self.tciInterface.stop_client()

        if self.selectedOperationalInterface is OperationalInterface.UDP:  # UDP server still running in fallback
            self.udpInterface.stop_server()
        elif self.selectedOperationalInterface is OperationalInterface.TCI:  # TCI client still running in fallback?
            self.tciInterface.stop_client()

    def close_current_operational_interface_for_fallback(self):
        if self.currentOperationalInterface is OperationalInterface.CAT:
            self.catInterface.close_device()
        # DO NOT STOP UDP SERVER OR ELSE THERE WILL NOTHING RECEIVED TO RECOVER FROM FALLBACK

    def switch_operational_interface(self, new_operational_interface=None):
        self.close_current_operational_interface()
        # open new operational interface
        if new_operational_interface is None:
            new_operational_interface = self.determine_next_operational_interface()
        self.selectedOperationalInterface = new_operational_interface
        self.open_operational_interface(new_operational_interface)

    def determine_next_operational_interface(self):
        if self.selectedOperationalInterface is OperationalInterface.UNIVERSAL:
            if self.catInterface.is_configured():
                next_operational_interface = OperationalInterface.CAT
            else:
                next_operational_interface = OperationalInterface.UDP
        elif self.selectedOperationalInterface is OperationalInterface.CAT:
            next_operational_interface = OperationalInterface.UDP
        elif self.selectedOperationalInterface is OperationalInterface.UDP:
            if self.tciInterface.is_configured():
                next_operational_interface = OperationalInterface.TCI
            else:
                next_operational_interface = OperationalInterface.UNIVERSAL
        else:
            next_operational_interface = OperationalInterface.UNIVERSAL
        return next_operational_interface

    def open_univ(self):
        self.currentOperationalInterface = OperationalInterface.UNIVERSAL

    def open_udp(self, from_fallback=False):
        if not from_fallback:
            self.udpInterface.reset_frequency()
            self.udpInterface.start_server()
        self.currentOperationalInterface = OperationalInterface.UDP
        if self.udpInterface.get_frequency() is None:
            self.fallback()

    def open_tci(self, from_fallback=False):
        if not from_fallback:
            self.tciInterface.reset_frequency()
            self.tciInterface.start_client()
        self.currentOperationalInterface = OperationalInterface.TCI
        if self.tciInterface.get_frequency() is None:
            self.fallback()

    def open_cat(self):
        self.currentOperationalInterface = OperationalInterface.CAT
        self.catInterface.open_device()
        if not self.catInterface.isOpen:
            self.fallback()

    def update_operational_interface(self):
        self.update_operational_interface_display_name()
        interface.set_operational_interface(self.currentOperationalInterface.value)
        self.get_and_push_frequency()
        if self.is_fallback():
            self.errorString = 'No {} available'.format(self.selectedOperationalInterface.name)
        else:
            self.errorString = ''
        self.errorStringVar.set(self.errorString)

    def update_operational_interface_display_name(self):
        self.currentOperationalInterfaceDisplayName.set(self.currentOperationalInterface.name[:4])

    def fallback(self):
        self.close_current_operational_interface_for_fallback()
        self.open_univ()

    def is_fallback(self):
        return self.selectedOperationalInterface is not self.currentOperationalInterface

    def try_restore(self):
        if self.selectedOperationalInterface == OperationalInterface.UDP:
            if self.udpInterface.get_frequency() is not None:
                self.open_udp(True)
        if self.selectedOperationalInterface == OperationalInterface.TCI:
            if self.tciInterface.get_frequency() is not None:
                self.open_tci(True)
        if self.selectedOperationalInterface == OperationalInterface.CAT:
            if self.catInterface.test_frequency(self.catInterface.rigData) is not None:
                self.open_cat()
        self.update_operational_interface()


    def get_and_push_frequency(self):
        if self.currentOperationalInterface == OperationalInterface.CAT:
            frequency = self.catInterface.get_frequency()
        elif self.currentOperationalInterface == OperationalInterface.UDP:
            frequency = self.udpInterface.get_frequency()
        elif self.currentOperationalInterface == OperationalInterface.TCI:
            frequency = self.tciInterface.get_frequency()
        else:
            # do nothing in UNIVERSAL mode
            return
        if frequency is not None:
            old_freq = Data.getInstance().f_m
            if old_freq != frequency:
                interface.set_cat_frq(frequency)
        else:
            self.fallback()
