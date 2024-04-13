from tkinter import *
from tkinter import ttk

from menu import window_elements
from operational_interface.catSupport import SupportedManufacturer, SupportedRig
from operationalInterface import OperationalInterfaceControl
from config import Config
from operationalInterface import OperationalInterface

NO_FREQUENCY = 'No frequency'

SELECT_RIG_DEFAULT = 'select RIG'


class InterfaceGeneralTab(ttk.Frame):
    def __init__(self, delegate, container):
        super().__init__(container)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.delegate = delegate

        container = ttk.Frame(self, pad=30)
        container.grid_propagate(True)
        container.grid(row=0, column=0, sticky="wnes")
        container.rowconfigure(1, weight=1)
        container.columnconfigure(0, weight=1)
        container.configure(borderwidth=5)

        selection_container = ttk.Frame(container)
        selection_container.grid_propagate(True)
        selection_container.grid(row=0, column=0, sticky="wnes")
        selection_container.columnconfigure(0, weight=1)
        selection_container.columnconfigure(4, weight=1)

        ttk.Label(selection_container, text="Default operational interface").grid(row=0, column=0, sticky='W', padx=20)

        self.radioButtonsByOperationalInterface = dict()
        for operational_interface in list(OperationalInterface):
             button = window_elements.create_radio_button_with_text(selection_container,
                                                                    text=operational_interface.name,
                                                                    variable=Config.get_instance().operationalInterfaceVar,
                                                                    command=self.on_default_operational_interface_changed,
                                                                    value=operational_interface.name)
             button.grid(row=operational_interface.value+1, column=0, sticky='W', padx=20, pady=5)
             self.radioButtonsByOperationalInterface[operational_interface] = button

        self.refresh_button_states()

        bottom_container = ttk.Frame(container)
        bottom_container.grid_propagate(True)
        bottom_container.grid(row=1, column=0, sticky="wnes")
        bottom_container.rowconfigure(1, weight=1)
        bottom_container.columnconfigure(2, weight=1)

        self.createCloseButton(bottom_container)

    def refresh_button_states(self):
        # CAT button
        if OperationalInterfaceControl.operationalInterface.catInterface.is_configured():
            self.radioButtonsByOperationalInterface[OperationalInterface.CAT].configure(state="normal")
        else:
            self.radioButtonsByOperationalInterface[OperationalInterface.CAT].configure(state="disabled")
        # TCI button
        if OperationalInterfaceControl.operationalInterface.tciInterface.is_configured():
            self.radioButtonsByOperationalInterface[OperationalInterface.TCI].configure(state="normal")
        else:
            self.radioButtonsByOperationalInterface[OperationalInterface.TCI].configure(state="disabled")

    def on_default_operational_interface_changed(self):
        Config.get_instance().saveOperationalInterface()

    def createCloseButton(self, container):
        ttk.Button(container, text="Close", pad=(40, 20), style="Settings.TButton",
                   command=self.onCloseClicked) \
            .grid(row=1, column=5, sticky="se")

    def onCloseClicked(self):
        self.delegate.onCloseClicked()


