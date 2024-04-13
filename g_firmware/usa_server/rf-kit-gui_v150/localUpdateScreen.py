from tkinter import *
from tkinter import ttk, messagebox

import re
import os

from cursorSetting import CursorSetting
from dimensions import DIMENSIONS
from sleepTimer import SleepTimer


class LocalUpdateScreen(Toplevel):

    def __init__(self, actual_version, min_version, delegate, container):
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

        self.delegate = delegate

        self.availableVersion = 0
        self.updateFilepath = None
        self.setAvailableVersionAndFilepath()

        self.container = ttk.Frame(self, pad=30)
        self.container.grid_propagate(False)
        self.container.grid(row=0, column=0, sticky="wnes")

        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.createVersionsAndUpdateButton(actual_version, min_version)

    def setAvailableVersionAndFilepath(self):
        pattern = re.compile("firmware\d+\.bin")
        for filepath in os.listdir("."):
            if pattern.match(filepath):
                version = int(re.search(r'\d+', filepath).group())
                self.availableVersion = version
                self.updateFilepath = filepath
                return

    def createVersionsAndUpdateButton(self, actual_version, min_version):
        container = ttk.Frame(self.container)
        for row in range(4):
            container.rowconfigure(row, weight=1, uniform="fred")
        container.columnconfigure(0, weight=1)
        container.grid(row=0, column=0, sticky="wnes")
        ttk.Label(container, text="Installed Version: {:s}".format(str(actual_version)), anchor="center").grid(row=0, column=0, sticky="wnes")
        ttk.Label(container, text="Available Version: {:s}".format(str(self.availableVersion)), anchor="center").grid(row=1, column=0, sticky="wnes")
        ttk.Label(container, text="Minimum Version: {:s}".format(str(min_version)), anchor="center").grid(row=2, column=0, sticky="wnes")
        updateButton = ttk.Button(container, text="Update", pad=(40, 20), style="Settings.TButton", command=self.onUpdateClicked)
        if actual_version >= self.availableVersion or min_version > self.availableVersion:
            updateButton.state([("disabled")])
        updateButton.grid(row=3, column=0)

    def onUpdateClicked(self):
        self.delegate.onUpdateClicked(self, self.updateFilepath, True)

    def onUpdateFailed(self):
        messagebox.showerror(parent=self, title="Update failed", message="An error occurred while updating.")

    def onUpdateFinished(self):
        self.destroy()
        # window has to be removed from cursor management to prevent errors on next cursor change
        CursorSetting.get_instance().stop_managing_cursor_for(self)
        SleepTimer.get_instance().stop_observing(self)
