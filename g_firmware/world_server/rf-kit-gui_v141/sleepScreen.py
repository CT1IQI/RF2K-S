from tkinter import ttk, Toplevel, FALSE

import themes
from dimensions import DIMENSIONS

from cursorSetting import CursorSetting


class SleepScreen(Toplevel):

    def __init__(self, container, wakeup_callback):
        self.previousTheme = themes.getCurrentTheme()
        self.wakeupCallback = wakeup_callback

        themes.useDarkTheme()
        super().__init__(container)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # get cursor managed
        CursorSetting.get_instance().manage_cursor_for(self)

        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.resizable(FALSE, FALSE)
        self.geometry(f"{DIMENSIONS.APP_WIDTH}x{DIMENSIONS.APP_HEIGHT}")

        ttk.Button(self, text="Touch to wake up", command=self.wakeup, style="Huge.TButton").grid(row=0, column=0, sticky="nwes")

    def wakeup(self):
        self.destroy()
        # window has to be removed from cursor management to prevent errors on next cursor change
        CursorSetting.get_instance().stop_managing_cursor_for(self)
        themes.useTheme(self.previousTheme)
        self.wakeupCallback()



