from tkinter import ttk

from menu.lazyNotebook import LazyNotebook
from menu.tabs.calibration_tab.potiConfigTab import PotiConfigTab
from menu.tabs.calibration_tab.offsetCalibrationTab import OffsetCalibrationTab


class CalibrationTab(ttk.Frame):

    def __init__(self, delegate, container):
        super().__init__(container)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.delegate = delegate

        self.lazyNotebook = None
        self.lazyOffsetCalibrationTab = None
        self.createMenu()

    def createMenu(self):
        self.lazyNotebook = LazyNotebook(self)
        self.lazyNotebook.grid(row=0, column=0, sticky="wnes")
        self.lazyNotebook.add(lambda master: PotiConfigTab(self, master), "Poti Config")
        self.lazyOffsetCalibrationTab = self.lazyNotebook.add(lambda master: OffsetCalibrationTab(self, master), "Power Meter Calibration")

    def onCloseClicked(self):
        self.delegate.onCloseClicked()
