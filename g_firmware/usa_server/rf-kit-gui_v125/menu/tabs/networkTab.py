
from tkinter import ttk

from menu.lazyNotebook import LazyNotebook
from menu.tabs.network_tab.lanTab import LanTab
from menu.tabs.network_tab.vncConfigTab import VncConfigTab
from menu.tabs.network_tab.wifiTab import WifiTab


class NetworkTab(ttk.Frame):

    def __init__(self, delegate, container):
        super().__init__(container)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.delegate = delegate
        self.create_notebook()

    def create_notebook(self):
        lazy_notebook = LazyNotebook(self)
        lazy_notebook.add(lambda master: VncConfigTab(self, master), "VNC Config")
        lazy_notebook.add(lambda master: LanTab(self, master), "LAN")
        lazy_notebook.add(lambda master: WifiTab(self, master), "WiFi")
        lazy_notebook.grid(row=0, column=0, sticky="wnes")

    def onCloseClicked(self):
        self.delegate.onCloseClicked()
