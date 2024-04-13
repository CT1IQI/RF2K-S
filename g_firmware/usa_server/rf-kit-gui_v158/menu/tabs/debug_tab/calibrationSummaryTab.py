from tkinter import ttk

from data import Data
from menu.lazyNotebook import LazyNotebook
from menu.tabs.debug_tab.calibration_summary_tab.biasCalibrationTab import BIASCalibrationTab
from menu.tabs.debug_tab.calibration_summary_tab.debugCalibrationTab import DebugCalibrationTab
from debug.debugCalibrationEnums import DebugCalibrationType
from menu.tabs.debug_tab.calibration_summary_tab.inputCalibrationTab import InputCalibrationTab


class CalibrationSummaryTab(ttk.Frame):

    def __init__(self, delegate, container):
        super().__init__(container)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.delegate = delegate

        self.lazyNotebook = None
        self.create_notebook()

    def create_notebook(self):
        self.lazyNotebook = LazyNotebook(self)
        self.lazyNotebook.grid(row=0, column=0, sticky="wnes")
        self.lazyNotebook.add(lambda master: InputCalibrationTab(self, master), "Input (Offset) Calibration", lambda tab: tab.update_all_digits())
        self.lazyNotebook.add(lambda master: DebugCalibrationTab(self, master, DebugCalibrationType.BIAS), "BIAS Calibration", lambda tab: tab.update_all_digits())
        self.lazyNotebook.add(lambda master: BIASCalibrationTab(self, master), "Output Power Calibration", lambda tab: self.on_output_tab_activated(tab))


    def on_output_tab_activated(self, output_tab):
        try:
            Data.getInstance().updateBIASPercentage()
            output_tab.activateFilter(Data.getInstance().filter)
        except ValueError:
            pass

    def onCloseClicked(self):
        self.delegate.onCloseClicked()
