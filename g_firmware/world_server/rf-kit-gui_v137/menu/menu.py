from tkinter import *
from tkinter import ttk

from dimensions import DIMENSIONS
from mainScreenTypeSetting import MainScreenTypeSetting
from menu.lazyNotebook import LazyNotebook
from menu.tabs.antennaTab import Antennas
from menu.tabs.settingsTab import SettingsTab
from menu.tabs.updateTab import UpdateTab
from menu.tabs.calibrationTab import CalibrationTab
from menu.tabs.networkTab import NetworkTab
from menu.tabs.interfaceTab import InterfaceTab
from menu.tabs.debugTab import DebugTab
from data import Data
from cursorSetting import CursorSetting

from interface import InterfaceWrapper
from sleepTimer import SleepTimer


class Menu(Toplevel):

    def __init__(self, main_delegate, container):
        super().__init__(container)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # get cursor managed
        CursorSetting.get_instance().manage_cursor_for(self)
        SleepTimer.get_instance().observe(self)

        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.resizable(FALSE, FALSE)
        self.geometry(f"{DIMENSIONS.APP_WIDTH}x{DIMENSIONS.APP_HEIGHT}")

        self.mainDelegate = main_delegate

        self.fetchDataJob = None

        self.lazyNotebook = None
        self.lazyCalibrationTab = None
        self.lazyDebugTab = None
        self.createMenu()

        self.fetchData()  # TODO move this also to Data class

    def createMenu(self):
        self.lazyNotebook = LazyNotebook(self)
        self.lazyNotebook.grid(row=0, column=0, sticky="wnes")
        self.lazyNotebook.add(lambda master: SettingsTab(self, master), "Settings", lambda tab: tab.lazy_tuner_notebook.on_tab_changed())
        self.lazyNotebook.add(lambda master: Antennas(self, master), "Antennas")
        self.lazyNotebook.add(lambda master: UpdateTab(self, master), "Update")
        self.lazyCalibrationTab = self.lazyNotebook.add(lambda master: CalibrationTab(self, master), "Calibration")
        self.lazyNotebook.add(lambda master: NetworkTab(self, master), "Network")
        self.lazyNotebook.add(lambda master: InterfaceTab(self, master), "Interface", lambda tab: tab.lazyNotebook.on_tab_changed())
        if self.mainDelegate.debugMode:
            self.lazyDebugTab = self.lazyNotebook.add(lambda master: DebugTab(self, master), "Debug", lambda tab: tab.lazyNotebook.on_tab_changed())

    def onCloseClicked(self):
        self.cancelFetchData()
        MainScreenTypeSetting.get_instance().apply(self.mainDelegate)
        self.destroy()
        # window has to be removed from cursor management to prevent errors on next cursor change
        CursorSetting.get_instance().stop_managing_cursor_for(self)
        SleepTimer.get_instance().stop_observing(self)
        self.mainDelegate.onMenuClose()

    def onUpdateClicked(self, updateDelegate):
        self.updateDelegate = updateDelegate
        self.cancelFetchData()
        self.mainDelegate.onUpdateClicked(self)

    def onUpdateFailed(self):
        self.fetchData()

        self.updateDelegate.onUpdateFailed()

    def onUpdateFinished(self):
        self.updateDelegate.onUpdateFinished()
        # Normally the handling of `this` would be before the updateDelegate handling
        # but we destroy the app and restart the app again, so it has to be done afterwards
        self.destroy()
        # window has to be removed from cursor management to prevent errors on next cursor change
        CursorSetting.get_instance().stop_managing_cursor_for(self)
        SleepTimer.get_instance().stop_observing(self)

    def onCloseApplication(self):
        self.mainDelegate.onCloseApplication()

    def fetchData(self):
        currentNotebookIndex = self.lazyNotebook.index(self.lazyNotebook.select())
        if currentNotebookIndex == 3:
            if self.lazyCalibrationTab.content:
                currentCalibrationIndex = self.lazyCalibrationTab.content.lazyNotebook.index(self.lazyCalibrationTab.content.lazyNotebook.select())
                try:
                    if currentCalibrationIndex == 1:
                        Data.getInstance().updateAll()
                        if self.lazyCalibrationTab.content.lazyOffsetCalibrationTab.content:
                            self.lazyCalibrationTab.content.lazyOffsetCalibrationTab.content.activateFilter(Data.getInstance().filter)
                    else:
                        Data.getInstance().updateAll()
                except ValueError:
                    pass
        else:
            if self.mainDelegate.debugMode and self.lazyDebugTab.content:
                self.lazyDebugTab.content.frqCountVar.set(InterfaceWrapper.getInstance().get_frq_count())
            Data.getInstance().updateAll()
        self.fetchDataJob = self.after(20, self.fetchData)

    def cancelFetchData(self):
        if self.fetchDataJob is None:
            return
        self.after_cancel(self.fetchDataJob)
        self.fetchDataJob = None
