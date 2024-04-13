from tkinter import *
from tkinter import ttk

from keyboard.numberKeyboard import NumberKeyboard
from menu import window_elements
from operationalInterface import OperationalInterfaceControl
from config import Config
from operational_interface.udpSupport import RadioMode

NO_FREQUENCY = 'No frequency'

SELECT_RIG_DEFAULT = 'select RIG'


class UdpTab(ttk.Frame):
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
        selection_container.columnconfigure(3, weight=1)

        self.udpInterface = OperationalInterfaceControl.operationalInterface.udpInterface

        self.appliedPort = Config.get_instance().udpConfig["port"]
        self.selectedPort = IntVar(value=self.appliedPort, name='selectedPort')
        self.create_port_selection(selection_container)
        self.appliedRadioMode = self.udpInterface.get_radio_mode()
        self.appliedFixedRadio = self.udpInterface.get_fixed_radio()
        self.selectedRadioMode = StringVar(value=self.appliedRadioMode.displayName)
        self.selectedFixedRadio = StringVar(value=self.appliedFixedRadio)
        self.create_radio_selection(selection_container)

        bottom_container = ttk.Frame(container)
        bottom_container.grid_propagate(True)
        bottom_container.grid(row=1, column=0, sticky="wnes")
        bottom_container.rowconfigure(1, weight=1)
        bottom_container.columnconfigure(2, weight=1)

        self.saveButton = None
        self.createSaveButton(bottom_container)
        self.createCloseButton(bottom_container)


    def create_port_selection(self, container):
        ttk.Label(container, text="Port").grid(row=0, column=0, padx=20, pady=20, sticky='NE')
        spinbox_container = window_elements.create_custom_spinbox_container(container, self.selectedPort)
        spinbox_container.grid(row=0, column=1, pady=20, padx=60, sticky='W')

    def create_radio_selection(self, container):
        ttk.Label(container, text="Listen to").grid(row=1, column=0, padx=20, sticky='NE')
        mode_container = ttk.Frame(container)
        mode_container.grid(row=1, column=1, padx=20, sticky='W')

        window_elements.create_radio_button_with_text(mode_container, text=RadioMode.ACTIVE.displayName,
                                                      variable=self.selectedRadioMode,
                                                      value=RadioMode.ACTIVE.displayName).grid(row=1, column=0, sticky='W')
        fixed_radio_container = ttk.Frame(mode_container)
        fixed_radio_container.grid(row=2, column=0)
        window_elements.create_radio_button_with_text(fixed_radio_container, text=RadioMode.FIXED.displayName,
                                                      variable=self.selectedRadioMode,
                                                      value=RadioMode.FIXED.displayName).grid(row=0, column=0, sticky='W')
        ttk.Combobox(fixed_radio_container, textvariable=self.selectedFixedRadio, values=["1", "2", "3", "4"],
                     state="readonly", height=9, width=3).grid(row=0, column=1, pady=15, padx=20)



    def createCloseButton(self, container):
        ttk.Button(container, text="Close", pad=(40, 20), style="Settings.TButton",
                   command=self.onCloseClicked) \
            .grid(row=1, column=5, sticky="se")

    def createSaveButton(self, container):
        self.saveButton = window_elements.create_responding_menu_button(container, "Save", self.onSaveClicked)
        self.saveButton.grid(row=1, column=4, sticky="se")

    def onCloseClicked(self):
        self.selectedPort.set(self.appliedPort)
        self.selectedRadioMode.set(self.appliedRadioMode.displayName)
        self.selectedFixedRadio.set(self.appliedFixedRadio)
        self.delegate.onCloseClicked()

    def onSaveClicked(self):
        self.appliedPort = self.selectedPort.get()
        self.appliedRadioMode = RadioMode.by_display_name().get(self.selectedRadioMode.get())
        self.appliedFixedRadio = self.selectedFixedRadio.get()
        Config.get_instance().udpConfig["port"] = self.appliedPort
        Config.get_instance().udpConfig["radio_mode"] = self.appliedRadioMode.displayName
        Config.get_instance().udpConfig["fixed_radio"] = self.appliedFixedRadio
        self.udpInterface.set_port(self.appliedPort)
        self.udpInterface.set_radio_mode(self.appliedRadioMode)
        self.udpInterface.set_fixed_radio(self.appliedFixedRadio)
        self.udpInterface.apply()
        Config.get_instance().save_udp_config()
