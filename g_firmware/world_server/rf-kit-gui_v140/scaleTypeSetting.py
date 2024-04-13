from tkinter import StringVar

from config import Config

DISPLAY_STANDARD = "Standard"
DISPLAY_NEEDLE = "Needle Scale"

class ScaleTypeSetting:

    instance = None

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            # init instance
            cls.instance = ScaleTypeSetting()
        return cls.instance


    def __init__(self):
        self.barScaleArgument = None
        self.needleScaleArgument = None
        self.scaleSetter = lambda arg: {}

    def initialize_scale_setter(self, scale_setter, bar_scale_argument, needle_scale_argument):
        self.barScaleArgument = bar_scale_argument
        self.needleScaleArgument = needle_scale_argument
        self.scaleSetter = scale_setter
        self.apply(Config.get_instance().scaleTypeVar.get())

    def change_display_type(self):
        if Config.get_instance().scaleTypeVar.get() == DISPLAY_STANDARD:
            new_type = DISPLAY_NEEDLE
        else:
            new_type = DISPLAY_STANDARD
        self.apply(new_type)
        Config.get_instance().scaleTypeVar.set(new_type)
        Config.get_instance().save_scale_type()


    def apply(self, display_type):
        if display_type == DISPLAY_STANDARD:
            self.scaleSetter(self.barScaleArgument)
        else:
            self.scaleSetter(self.needleScaleArgument)

