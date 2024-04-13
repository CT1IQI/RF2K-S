from tkinter import ttk, INSERT, StringVar


class Key:

    def __init__(self, value, shift_value=None, action=lambda current_value, entry: entry.insert(INSERT, current_value)):
        self.value = value
        self.shiftValue = shift_value
        self.action = action
        self.useShiftValue = False
        self.currentValue = None

    def shift(self):
        if self.shiftValue is not None:
            self.useShiftValue = not self.useShiftValue
            if self.currentValue is None:
                return
            if self.useShiftValue:
                self.currentValue.set(self.shiftValue)
            else:
                self.currentValue.set(self.value)

    def create_button(self, container, row, column, entry):
        self.currentValue = StringVar(container, self.value)
        if self.useShiftValue:
            self.currentValue.set(self.shiftValue)
        button = ttk.Label(container, textvariable=self.currentValue, anchor="center", pad=10, style="Keyboard.TLabel")
        button.grid(row=row, column=column, padx=1, pady=1, sticky="wnes")
        button.bind("<ButtonRelease-1>", lambda event: self.on_button_pressed(entry))

    def on_button_pressed(self, entry):
        self.action(self.currentValue.get(), entry)
        entry.focus_set()


class LetterKey(Key):

    def __init__(self, value):
        Key.__init__(self, value.lower(), value.upper())
