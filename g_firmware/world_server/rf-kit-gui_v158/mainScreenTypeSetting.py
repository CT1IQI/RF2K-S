from enum import Enum
from tkinter import StringVar

from contestDisplay import ContestDisplay


class MainScreenType(Enum):
    STANDARD = "Standard"
    CONTEST = "Contest"


class MainScreenTypeSetting:
    instance = None

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            # init instance
            cls.instance = MainScreenTypeSetting()
        return cls.instance

    def __init__(self):
        self.selectedMainScreen = MainScreenType.STANDARD
        self.currentMainScreen = MainScreenType.STANDARD
        self.currentMainScreenStringVar = StringVar(value=self.selectedMainScreen.value)
        self.contestDisplay = None

    def change_main_screen(self):
        if self.selectedMainScreen == MainScreenType.STANDARD:
            self.selectedMainScreen = MainScreenType.CONTEST
        else:
            self.selectedMainScreen = MainScreenType.STANDARD
        self.currentMainScreenStringVar.set(self.selectedMainScreen.value)

    def apply(self, main_window):
        if self.selectedMainScreen is not self.currentMainScreen:
            if self.selectedMainScreen is MainScreenType.STANDARD:
                self.close_contest_display()
            else:
                self.open_contest_display(main_window)
            self.currentMainScreen = self.selectedMainScreen

    def open_contest_display(self, main_window):
        if self.contestDisplay is None:
            self.contestDisplay = ContestDisplay(main_window)

    def close_contest_display(self):
        if self.contestDisplay is not None:
            self.contestDisplay.close()
            self.contestDisplay = None
