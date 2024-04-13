from enum import Enum
from tkinter import *
from tkinter import ttk

from dimensions import DIMENSIONS


class RestartMessage(Enum):
    UPDATED = "Update successful.\n\nPlease shut down the device and wait at least 30 seconds before restarting it."
    SYSTEM_CONFIG_APPLIED = "System configuration updated.\n\nPlease restart the device."

    def __str__(self):
        return self.value


class RestartScreen(Toplevel):

    def __init__(self, message:RestartMessage, container):
        super().__init__(container)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Remove cursor
        self.config(cursor="none")

        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.resizable(FALSE, FALSE)
        self.geometry(f"{DIMENSIONS.APP_WIDTH}x{DIMENSIONS.APP_HEIGHT}")

        container = ttk.Frame(self)
        container.grid(row=0, column=0)
        ttk.Label(container, text=message, justify="center").grid(row=0, column=0)

