import os

from interface import InterfaceWrapper
from enums import Generation


class Display:
    instance = None

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            # init instance
            cls.instance = Display()
        return cls.instance

    def __init__(self):
        self.onFunction = None
        self.offFunction = None

    def init_for_generation(self, generation):
        if generation == Generation.RF2K_PLUS:
            self.onFunction = lambda: os.system('vcgencmd display_power 1')
            self.offFunction = lambda: os.system('vcgencmd display_power 0')
        else:
            self.onFunction = InterfaceWrapper.getInstance().display_on
            self.offFunction = InterfaceWrapper.getInstance().display_off

    def on(self):
        self.onFunction()

    def off(self):
        self.offFunction()
