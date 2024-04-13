from tkinter import ttk, StringVar

from keyboard.keyboard import Keyboard
from menu import window_elements


class SecretKeyboard(Keyboard):
    def __init__(self, container, textvariable, onOKClickedHandler, validating_method = None, validation_error_message = None):
        super(SecretKeyboard, self).__init__(container, textvariable, onOKClickedHandler, validating_method, validation_error_message)
        #self.entry.configure(show="*")
        self.showVar = StringVar(self, '*')
        window_elements.create_check_button_with_text(self, text='show password', variable=self.showVar, onvalue='',
                        offvalue='*', command=self.configure_entry_show).grid(row=2, column=0)
        self.configure_entry_show()

    def configure_entry_show(self):
        self.entry.configure(show=self.showVar.get())
