from tkinter import *
from tkinter import ttk, END

from enum import Enum

from cursorSetting import CursorSetting
from keyboard.key import Key, LetterKey

from dimensions import DIMENSIONS
from sleepTimer import SleepTimer


class NumberKeyboard(Toplevel):

    def __init__(self, container, intvariable, onOKClickedHandler=lambda: None):
        super().__init__(container)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        # get cursor managed
        CursorSetting.get_instance().manage_cursor_for(self)
        SleepTimer.get_instance().observe(self)

        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.resizable(FALSE, FALSE)
        self.geometry(f"{DIMENSIONS.APP_WIDTH}x{DIMENSIONS.APP_HEIGHT}")

        self.intvariable = intvariable
        self.textvariable = StringVar(value=str(self.intvariable.get()))
        self.onOKClickedHandler = onOKClickedHandler

        self.buttonRows = 4
        self.buttonColumns = 15
        self.characterButtons = []

        self.keys = [
            [Key("7"), Key("8"), Key("9"), Key("⇦", action=self.on_backspace_clicked)],
            [Key("4"), Key("5"), Key("6")],
            [Key("1"), Key("2"), Key("3")],
            [Key("0"), Key("←", action=self.on_left_clicked), Key("→", action=self.on_right_clicked)]]

        self.entry = None
        self.display()

    def on_shift_clicked(self, current_value, entry):
        for row in self.keys:
            for key in row:
                key.shift()

    def on_backspace_clicked(self, current_value, entry):
        entry.delete(entry.index(INSERT)-1, INSERT)

    def on_left_clicked(self, current_value, entry):
        entry.icursor(max(entry.index(INSERT)-1, 0))

    def on_right_clicked(self, current_value, entry):
        entry.icursor(min(entry.index(INSERT)+1, entry.index(END)))

    def display(self):
        self.entry = ttk.Entry(self, textvariable=self.textvariable, font=("Lato", 24))
        self.entry.grid(row=1, column=0, padx=20, sticky="wnes")
        self.entry.icursor(self.entry.index(END))
        self.entry.focus_set()

        container = ttk.Frame(self)
        container.grid(row=3, column=0, sticky="wnes")

        index_r = 0
        for row in self.keys:
            container.rowconfigure(index_r, weight=1, uniform="fred")
            index_c = 0
            for key in row:
                container.columnconfigure(index_c, weight=1, uniform="fred")
                key.create_button(container, index_r, index_c, self.entry)
                index_c = index_c + 1
            index_r = index_r + 1

        bottom_container = ttk.Frame(self, padding=40)
        bottom_container.grid_propagate(True)
        bottom_container.grid(row=4, column=0, sticky="wnes")
        bottom_container.columnconfigure(0, weight=1)
        ttk.Button(bottom_container, text="OK", pad=(40, 20), style="Settings.TButton", command=self.onOKClicked) \
            .grid(row=0, column=1, sticky="se")

    def onOKClicked(self):
        self.intvariable.set(int(self.textvariable.get()))
        self.destroy()
        # window has to be removed from cursor management to prevent errors on next cursor change
        CursorSetting.get_instance().stop_managing_cursor_for(self)
        SleepTimer.get_instance().stop_observing(self)
        self.onOKClickedHandler()
