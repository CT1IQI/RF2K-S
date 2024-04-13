from tkinter import ttk, Toplevel, FALSE

import themes
from data import Data
from dimensions import DIMENSIONS

from cursorSetting import CursorSetting
from main_screen.operating_buttons import OperatingButtons
from main_screen.scale import BarScale
from main_screen.status import StatusBar
from sleepTimer import SleepTimer


class ContestDisplay(Toplevel):

    def __init__(self, main_screen):
        super().__init__(main_screen)

        self.mainScreenDelegate = main_screen

        self.configure(background="#000000")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        container = ttk.Frame(self)
        container.grid(row=0, column=0, pady=(0, 20), sticky="wnes")
        container.rowconfigure(0, weight=5, uniform="row")
        container.rowconfigure(1, weight=2, uniform="row")
        container.rowconfigure(2, weight=5, uniform="row")
        container.columnconfigure(0, weight=2)
        container.columnconfigure(1, weight=1)

        # get cursor managed
        CursorSetting.get_instance().manage_cursor_for(self)
        SleepTimer.get_instance().observe(self)

        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.resizable(FALSE, FALSE)
        self.geometry(f"{DIMENSIONS.APP_WIDTH}x{DIMENSIONS.APP_HEIGHT}")

        self.forward_scale = BarScale(container, only_forward=True)
        self.forward_scale.grid(row=0, column=0, columnspan=2, sticky="nwes")

        StatusBar(container, True, True).grid(row=1, column=0, columnspan=2, sticky="w")

        OperatingButtons(container, True).grid(row=2, column=0, sticky="nwes")


        menu = ttk.Label(container, text="Menu", anchor="center", pad=(10, 15), style="Large.Menu.TLabel")
        menu.bind("<ButtonRelease-1>", lambda _: self.on_menu_clicked(), True)
        menu.grid(row=2, column=1)

        self.update_idletasks()
        self.forward_scale.drawScaleAndBars()
        Data.getInstance().register_fetch_watcher(self.update_after_fetch)

    def update_after_fetch(self):
        self.forward_scale.update_scale()

    def on_menu_clicked(self):
        self.mainScreenDelegate.onMenuClicked()

    def close(self):
        Data.getInstance().unregister_fetch_watcher(self.update_after_fetch)
        self.destroy()
        # window has to be removed from cursor management to prevent errors on next cursor change
        CursorSetting.get_instance().stop_managing_cursor_for(self)
        SleepTimer.get_instance().stop_observing(self)


