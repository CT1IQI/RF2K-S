from tkinter import ttk, StringVar

from data import Data
from menu.lazyNotebook import LazyNotebook
from menu.tabs.debug_tab.biasCalibrationTab import BIASCalibrationTab
from menu.tabs.debug_tab.debugCalibrationTab import DebugCalibrationTab
from debug.debugCalibrationEnums import DebugCalibrationType
from menu.tabs.debug_tab.generalTab import GeneralTab


class DebugTab(ttk.Frame):

    def __init__(self, delegate, container):
        super().__init__(container)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.delegate = delegate

        self.frqCountVar = StringVar(value=0)

        self.lazyNotebook = None
        self.create_notebook()

    def create_notebook(self):
        self.lazyNotebook = LazyNotebook(self)
        self.lazyNotebook.grid(row=0, column=0, sticky="wnes")
        self.lazyNotebook.add(lambda master: GeneralTab(self, master), "General")
        self.lazyNotebook.add(lambda master: DebugCalibrationTab(self, master, DebugCalibrationType.BIAS), "BIAS Calibration", lambda tab: tab.update_all_digits())
        self.lazyNotebook.add(lambda master: DebugCalibrationTab(self, master, DebugCalibrationType.INPUT), "Input Calibration", lambda tab: tab.update_all_digits())
        self.lazyNotebook.add(lambda master: BIASCalibrationTab(self, master), "Output Power Calibration", lambda tab: self.on_output_tab_activated(tab))
        self.lazyNotebook.add(lambda master: DebugCalibrationTab(self, master, DebugCalibrationType.INPUT_OFFSET), "Input Offset Calibration", lambda tab: tab.update_all_digits())

    def on_output_tab_activated(self, output_tab):
        try:
            Data.getInstance().updateBIASPercentage()
            output_tab.activateFilter(Data.getInstance().filter)
        except ValueError:
            pass

    def onCloseClicked(self):
        self.delegate.onCloseClicked()

    def onCloseApplication(self):
        self.delegate.onCloseApplication()
