from tkinter import *
from tkinter import ttk

from menu import window_elements
from operational_interface.catSupport import SupportedManufacturer, SupportedRig
from operationalInterface import OperationalInterfaceControl
from config import Config

NO_FREQUENCY = 'No frequency'

SELECT_RIG_DEFAULT = 'select RIG'


class CatTab(ttk.Frame):
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

        self.catInterface = OperationalInterfaceControl.operationalInterface.catInterface

        self.appliedManufacturer = None if Config.get_instance().catConfig["manufacturer"] is None else SupportedManufacturer[Config.get_instance().catConfig["manufacturer"]]
        self.appliedRig = None if Config.get_instance().catConfig["rig"] is None else SupportedRig[Config.get_instance().catConfig["rig"]]
        self.appliedBaudRate = Config.get_instance().catConfig["baud_rate"]
        self.selectedManufacturerDisplayName = StringVar(value=self.appliedManufacturerDisplayNameOrDefault())
        self.selectedRigDisplayName = StringVar(value=self.appliedRigDisplayNameOrDefault())
        self.selectedBaudRateDisplayString = StringVar(value=self.appliedBaudRateOrDefault())
        self.testResultString = StringVar(name='testResultString')

        self.manOptions = SupportedManufacturer.by_display_name()
        self.create_manufacturer_selection(selection_container)

        self.rigOptions = dict() if self.selectedManufacturer() is None else SupportedRig.for_manufacturer_by_display_name(self.selectedManufacturer())

        self.rig_combobox = None
        self.create_rig_selection(selection_container)

        self.baudRateOptions = dict([(str(rate), rate) for rate in [2400, 4800, 9600, 19200, 38400, 57600, 115200]])
        self.create_baud_rate_selection(selection_container)

        bottom_container = ttk.Frame(container)
        bottom_container.grid_propagate(True)
        bottom_container.grid(row=1, column=0, sticky="wnes")
        bottom_container.rowconfigure(1, weight=1)
        bottom_container.columnconfigure(2, weight=1)

        self.testButton = None
        self.createTestButton(bottom_container)
        self.saveButton = None
        self.createSaveButton(bottom_container)
        self.testResultEntry = None
        self.createTestResultEntry(bottom_container)
        self.createCloseButton(bottom_container)

    def appliedRigDisplayNameOrDefault(self):
        return SELECT_RIG_DEFAULT if self.appliedRig is None else self.appliedRig.displayName

    def appliedManufacturerDisplayNameOrDefault(self):
        return 'select manufacturer' if self.appliedManufacturer is None else self.appliedManufacturer.displayName

    def appliedBaudRateOrDefault(self):
        return 'select baud rate' if self.appliedBaudRate is None else self.appliedBaudRate

    def create_manufacturer_selection(self, container):
        ttk.Label(container, text="Manufacturer").grid(row=0, column=1, padx=20, sticky='E')
        manufacturer_combobox = ttk.Combobox(container, textvariable=self.selectedManufacturerDisplayName, values=list(self.manOptions), state="readonly", height=9)
        manufacturer_combobox.bind("<<ComboboxSelected>>", self.on_man_change)
        manufacturer_combobox.grid(row=0, column=2, pady=5)

    def create_rig_selection(self, container):
        ttk.Label(container, text="RIG").grid(row=1, column=1, padx=20, sticky='E')
        self.rig_combobox = ttk.Combobox(container, textvariable=self.selectedRigDisplayName, values=list(self.rigOptions), state="disabled", height=7)
        self.rig_combobox.bind("<<ComboboxSelected>>", self.on_rig_change)
        self.rig_combobox.grid(row=1, column=2, pady=5)
        self.set_rig_menu_state()

    def set_rig_menu_state(self):
        if self.selectedManufacturer() is None:
            self.rig_combobox.configure(state="disabled")
        else:
            self.rig_combobox.configure(state="readonly")

    def create_baud_rate_selection(self, container):
        ttk.Label(container, text="baud rate").grid(row=3, column=1, padx=20, sticky='E')
        baud_rate_combobox = ttk.Combobox(container, textvariable=self.selectedBaudRateDisplayString, values=list(self.baudRateOptions), state="readonly", height=6)
        baud_rate_combobox.bind("<<ComboboxSelected>>", self.on_baud_rate_change)
        baud_rate_combobox.grid(row=3, column=2, pady=5)

    def on_man_change(self, event):
        man = self.selectedManufacturer()
        self.selectedRigDisplayName.set(SELECT_RIG_DEFAULT)
        self.rigOptions = SupportedRig.for_manufacturer_by_display_name(man)
        self.rig_combobox.configure(values=list(self.rigOptions))
        self.set_rig_menu_state()

        self.setTestButtonState()
        self.testResultString.set('')
        self.setSaveButtonState()

    def on_rig_change(self, event):
        self.setTestButtonState()
        self.testResultString.set('')
        self.setSaveButtonState()

    def on_baud_rate_change(self, event):
        self.setTestButtonState()
        self.testResultString.set('')
        self.setSaveButtonState()


    def createCloseButton(self, container):
        ttk.Button(container, text="Close", pad=(40, 20), style="Settings.TButton",
                   command=self.onCloseClicked) \
            .grid(row=1, column=5, sticky="se")

    def createTestResultEntry(self, container):
        self.testResultEntry = ttk.Entry(container, textvariable=self.testResultString, state="readonly",
                                         style='Status.TEntry', justify='center', font=("Lato", 24, "bold"),
                                         validatecommand=self.valid_frequency)
        self.testResultEntry.grid(row=1, column=2, sticky="se", padx=20)

    def valid_frequency(self):
        result_string_value = self.testResultString.get()
        return result_string_value and result_string_value != NO_FREQUENCY

    def createTestButton(self, container):
        self.testButton = window_elements.create_responding_menu_button(container, "Test", self.onTestClicked)
        self.testButton.grid(row=1, column=3, sticky="se")
        self.setTestButtonState()

    def setTestButtonState(self):
        if self.isValidSelection():
            self.testButton["state"] = "normal"
        else:
            self.testButton["state"] = "disabled"

    def createSaveButton(self, container):
        self.saveButton = window_elements.create_responding_menu_button(container, "Save", self.onSaveClicked)
        self.saveButton.grid(row=1, column=4, sticky="se")
        self.setSaveButtonState()

    def setSaveButtonState(self):
        if self.isValidSelection():
            self.saveButton["state"] = "normal"
        else:
            self.saveButton["state"] = "disabled"

    def isValidSelection(self):
        return (self.selectedManufacturer() is not None) and (self.selectedRig() is not None) and (self.selectedBaudRate() is not None)

    def onCloseClicked(self):
        self.selectedManufacturerDisplayName.set(self.appliedManufacturerDisplayNameOrDefault())
        self.selectedRigDisplayName.set(self.appliedRigDisplayNameOrDefault())
        self.testResultString.set('')
        self.setTestButtonState()
        self.delegate.onCloseClicked()

    def onTestClicked(self):
        frq = self.catInterface.test_rig_and_baud_rate(self.selectedRig(), self.selectedBaudRate())
        self.display_test_result(frq)

    def onSaveClicked(self):
        self.appliedManufacturer = self.selectedManufacturer()
        self.appliedRig = self.selectedRig()
        self.appliedBaudRate = self.selectedBaudRate()
        Config.get_instance().catConfig["manufacturer"] = self.appliedManufacturer.name
        Config.get_instance().catConfig["rig"] = self.appliedRig.name
        Config.get_instance().catConfig["baud_rate"] = self.appliedBaudRate
        self.catInterface.set_rig_and_baud_rate(self.appliedRig, self.appliedBaudRate)
        Config.get_instance().save_cat_config()

    def display_test_result(self, frq):
        result = NO_FREQUENCY
        if frq is not None:
            result = "{:d} kHz".format(int(frq // 1000))
        self.testResultString.set(result)
        #self.testResultEntry.configure('foreground', color)
        self.testResultEntry.validate()

    def selectedManufacturer(self):
        return self.manOptions.get(self.selectedManufacturerDisplayName.get())

    def selectedRig(self):
        return self.rigOptions.get(self.selectedRigDisplayName.get())

    def selectedBaudRate(self):
        return self.baudRateOptions.get(self.selectedBaudRateDisplayString.get())
