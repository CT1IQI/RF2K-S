from tkinter import ttk, SUNKEN

from menu.tabs.network_tab.vncConfigTab import VncConfigTab


class LazyNotebook(ttk.Notebook):
    def __init__(self, master, small=False):
        super().__init__(master, style="Small.Menu.TNotebook" if small else "Menu.TNotebook")
        self.bind("<<NotebookTabChanged>>", lambda _: self.on_tab_changed())
        self.tabs

    def add(self, lazy_init, name, activation_callback=None):
        lazy_tab = LazyTab(self, lazy_init, activation_callback)
        super().add(lazy_tab, text=name)
        return lazy_tab

    def on_tab_changed(self):
        self.nametowidget(self.tabs()[self.index("current")]).activate()


class LazyTab(ttk.Frame):
    def __init__(self, master, lazy_init, activation_callback):
        super().__init__(master)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.lazyInit = lazy_init
        self.content = None
        self.activationCallback = activation_callback

    def activate(self):
        if self.content is None:
            self.content = self.lazyInit(self)
            self.content.grid(row=0, column=0, sticky="wnes")
        if self.activationCallback is not None:
            self.activationCallback(self.content)
