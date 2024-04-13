from tkinter import *
from tkinter import ttk

from keyboard.keyboard import Keyboard
from keyboard.numberKeyboard import NumberKeyboard
from menu import window_elements
from operationalInterface import OperationalInterfaceControl
from config import Config
from operational_interface import tciSupport
from operational_interface.udpSupport import RadioMode

NO_FREQUENCY = 'No frequency'

SELECT_RIG_DEFAULT = 'select RIG'


class TciTab(ttk.Frame):
    def __init__(self, delegate, container):
        super().__init__(container)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.delegate = delegate

        container = ttk.Frame(self, pad=30)
        container.grid_propagate(True)
        container.grid(row=0, column=0, sticky="wnes")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.configure(borderwidth=5)

        self.selectionContainer = ttk.Frame(container)
        self.selectionContainer.grid_propagate(True)
        self.selectionContainer.grid(row=0, column=0, sticky="wnes")
        self.selectionContainer.columnconfigure(0, weight=1)
        self.selectionContainer.columnconfigure(3, weight=1)

        self.tciInterface = OperationalInterfaceControl.operationalInterface.tciInterface

        self.appliedHost = Config.get_instance().tciConfig.get("host")
        self.appliedPort = Config.get_instance().tciConfig["port"]
        self.selectedPort = IntVar(value=self.appliedPort, name='selectedPort')
        self.create_port_selection(self.selectionContainer)
        self.selectedHost = StringVar(value=self.appliedHost)
        self.create_host_selection(self.selectionContainer)

        bottom_container = ttk.Frame(container)
        bottom_container.grid_propagate(True)
        bottom_container.grid(row=1, column=0, sticky="wnes")
        bottom_container.rowconfigure(1, weight=1)
        bottom_container.columnconfigure(2, weight=1)

        self.saveButton = None
        self.createSaveButton(bottom_container)
        self.createCloseButton(bottom_container)

        if not tciSupport.is_websockets_installed():
            self.selectionContainer.grid_remove()
            self.installContainer = ttk.Frame(container)
            self.installContainer.grid_propagate(True)
            self.installContainer.grid(row=0, column=0)
            self.installButton = ttk.Button(self.installContainer, text="Install TCI", pad=(40, 20), style="Settings.TButton",
                                            command=self.install_tci)
            self.installButton.grid(row=1, column=0, pady=20)
            self.installErrorMessage = ttk.Label(self.installContainer, text="Installing TCI failed", style="Error.TLabel")

    def install_tci(self):
        self.installButton.grid_remove()
        self.installErrorMessage.grid_remove()
        install_message = ttk.Label(self.installContainer, text="Installing TCI...")
        install_message.grid(row=0, column=0)
        self.update_idletasks()

        success = tciSupport.install_websockets()

        install_message.grid_remove()
        if success:
            self.installContainer.grid_forget()
            self.selectionContainer.grid()
        else:
            self.installButton.grid()
            self.installErrorMessage.grid(row=0, column=0)



    def create_port_selection(self, container):
        ttk.Label(container, text="Port").grid(row=1, column=0, padx=20, pady=20, sticky='NE')
        spinbox_container = window_elements.create_custom_spinbox_container(container, self.selectedPort)
        spinbox_container.grid(row=1, column=1, pady=20, padx=60, sticky='W')

    def create_host_selection(self, container):
        ttk.Label(container, text="Host").grid(row=0, column=0, padx=20, sticky='NE')
        host_entry = ttk.Entry(container, textvariable=self.selectedHost, font=("Lato", 18), style="Config.TEntry")
        host_entry.grid(row=0, column=1, pady=20, padx=60, sticky='W')

        host_entry.bind("<ButtonRelease-1>", lambda e: Keyboard(self, self.selectedHost,
                                                              lambda: self.on_keyboard_ok))

    def on_keyboard_ok(self):
        pass

    def createCloseButton(self, container):
        ttk.Button(container, text="Close", pad=(40, 20), style="Settings.TButton",
                   command=self.onCloseClicked) \
            .grid(row=1, column=5, sticky="se")

    def createSaveButton(self, container):
        self.saveButton = window_elements.create_responding_menu_button(container, "Save", self.onSaveClicked)
        self.saveButton.grid(row=1, column=4, sticky="se")

    def onCloseClicked(self):
        self.selectedPort.set(self.appliedPort)
        self.selectedHost.set(self.appliedHost)
        self.delegate.onCloseClicked()

    def onSaveClicked(self):
        self.appliedHost = self.selectedHost.get()
        self.appliedPort = self.selectedPort.get()
        Config.get_instance().tciConfig["host"] = self.appliedHost
        Config.get_instance().tciConfig["port"] = self.appliedPort
        self.tciInterface.set_host(self.appliedHost)
        self.tciInterface.set_port(self.appliedPort)
        self.tciInterface.apply()
        Config.get_instance().save_tci_config()
