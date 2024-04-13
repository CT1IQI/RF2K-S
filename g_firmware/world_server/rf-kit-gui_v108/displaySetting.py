from tkinter import StringVar

import interface
from config import Config
from turnOffDisplayAskScreen import TurnOffDisplayAskScreen


class DisplaySetting:
    instance = None

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            # init instance
            cls.instance = DisplaySetting()
        return cls.instance

    def __init__(self):
        self.displayState = StringVar()

    def apply_on_startup(self, app):
        self.displayState.set('On')
        if not Config.get_instance().displayOn.get():
            TurnOffDisplayAskScreen(app, self.disable, self.change_state)

    def enable(self):
        self.displayState.set('On')
        interface.display_on()

    def disable(self):
        self.displayState.set('Off')
        interface.display_off()

    def change_state(self):
        Config.get_instance().displayOn.set(not Config.get_instance().displayOn.get())
        if Config.get_instance().displayOn.get():
            self.enable()
        else:
            self.disable()
        Config.get_instance().save_display_status()

