from tkinter import *
from tkinter import ttk

from menu.lazyNotebook import LazyNotebook
from menu.tabs.interface_tab.catTab import CatTab
from menu.tabs.interface_tab.generalTab import InterfaceGeneralTab
from menu.tabs.interface_tab.tciTab import TciTab
from menu.tabs.interface_tab.udpTab import UdpTab


class InterfaceTab(ttk.Frame):

    def __init__(self, delegate, container):
        super().__init__(container)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.delegate = delegate
        self.lazyNotebook = None
        self.createMenu()

    def createMenu(self):
        self.lazyNotebook = LazyNotebook(self)
        self.lazyNotebook.grid(row=0, column=0, sticky="wnes")
        self.lazyNotebook.add(lambda master: InterfaceGeneralTab(self, master), "General", lambda tab: tab.refresh_button_states())
        self.lazyNotebook.add(lambda master: CatTab(self, master), "CAT")
        self.lazyNotebook.add(lambda master: UdpTab(self, master), "UDP")
        self.lazyNotebook.add(lambda master: TciTab(self, master), "TCI")

    def onCloseClicked(self):
        self.delegate.onCloseClicked()
