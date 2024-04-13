from enum import Enum
from tkinter import *
from tkinter import ttk

from cursorSetting import CursorSetting
from dimensions import DIMENSIONS

import interface
import update
from sleepTimer import SleepTimer


class UpdateInProgress(Toplevel):

    class Stage(Enum):
        CONNECTING = 0
        DOWNLOAD_VERSIONS = 1
        DOWNLOAD_CONTROLLER = 2
        CHECK_HASH_CONTROLLER = 3
        DOWNLOAD_GUI = 4
        CHECK_HASH_GUI = 5
        UPDATE_CONTROLLER = 6
        UPDATE_GUI = 7
        SUCCESSFUL = 8

        def __str__(self):
            if self == self.CONNECTING:
                return "Connecting..."
            if self == self.DOWNLOAD_VERSIONS:
                return "Downloading versions..."
            if self == self.DOWNLOAD_CONTROLLER:
                return "Downloading new controller version..."
            if self == self.CHECK_HASH_CONTROLLER:
                return "Checking controller hash..."
            if self == self.DOWNLOAD_GUI:
                return "Downloading new GUI version..."
            if self == self.CHECK_HASH_GUI:
                return "Checking GUI hash..."
            if self == self.UPDATE_CONTROLLER:
                return "Updating controller..."
            if self == self.UPDATE_GUI:
                return "Updating GUI..."
            if self == self.SUCCESSFUL:
                return "Update successful."
            return ""

    def __init__(self, delegate, container, filepath=None):
        super().__init__(container)

        self.rowconfigure(0, weight=1, uniform="fred")
        self.rowconfigure(1, weight=1, uniform="fred")
        self.columnconfigure(0, weight=1)

        # get cursor managed
        CursorSetting.get_instance().manage_cursor_for(self)
        SleepTimer.get_instance().observe(self)

        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.resizable(FALSE, FALSE)
        self.geometry(f"{DIMENSIONS.APP_WIDTH}x{DIMENSIONS.APP_HEIGHT}")

        self.delegate = delegate
        self.filepath = filepath

        self.stage = self.Stage.CONNECTING
        self.progressLabelVar = StringVar(value=self.stage)

        ttk.Label(self, textvariable=self.progressLabelVar, anchor="center").grid(row=0, column=0, sticky="wse")
        self.progressVar = DoubleVar()
        self.progressBar = ttk.Progressbar(self, variable=self.progressVar, maximum=1)
        self.progressBar.grid(row=1, column=0, pady=(10, 0), padx=100, sticky="wne")

        self.after(1000, self.startUpdate)

    def startUpdate(self):
        # Check if local update or via internet
        if self.filepath is None:
            try:
                update.update_complete_software(self.onProgressUpdate)
                print("update completed successful.")
            except Exception as e:
                print("error occured during update process, try again. If this error remains, call support")
                self.onError()
                return
        else:
            try:
                interface.update(self.filepath, lambda p: self.onProgressUpdate(self.Stage.UPDATE_CONTROLLER, p))
            except Exception as e:
                self.onError()
                return
        self.destroy()
        # window has to be removed from cursor management to prevent errors on next cursor change
        CursorSetting.get_instance().stop_managing_cursor_for(self)
        SleepTimer.get_instance().stop_observing(self)
        self.delegate.onUpdateFinished()

    def onError(self):
        self.destroy()
        # window has to be removed from cursor management to prevent errors on next cursor change
        CursorSetting.get_instance().stop_managing_cursor_for(self)
        SleepTimer.get_instance().stop_observing(self)
        self.delegate.onUpdateFailed()

    def onProgressUpdate(self, stage, percentage):
        self.stage = stage
        self.progressLabelVar.set(self.stage)
        self.progressVar.set(percentage)
        self.update_idletasks()

