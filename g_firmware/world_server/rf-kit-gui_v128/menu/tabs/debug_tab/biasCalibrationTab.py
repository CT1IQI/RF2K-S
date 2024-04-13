from tkinter import *
from tkinter import ttk

from data import Data

import interface
from menu import window_elements


class BIASCalibrationTab(ttk.Frame):

    filters = ["6m", "15/12/10m", "20/17m", "40/30m", "80/60m", "160m"]

    def __init__(self, delegate, container):
        super().__init__(container)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.delegate = delegate

        self.incrementJob = None
        self.decrementJob = None

        self.activeFilter = None
        self.filterContainers = list()
        self.filterValueLabels = list()

        self.container = ttk.Frame(self, pad=(30, 0, 30, 30))
        self.container.grid_propagate(False)
        self.container.grid(row=0, column=0, sticky="wnes")

        for i in range(0, 7):
            self.container.rowconfigure(i, weight=1, uniform="fred")
        self.container.columnconfigure(0, weight=1)
        self.container.columnconfigure(1, weight=1)

        self.createFilters()
        self.createForwardPower()
        self.createSaveButton()
        self.createCloseButton()

    def createFilterAdjustmentContainer(self, container, filter):
        subcontainer = ttk.Frame(container, style="Sub.Calibration.TFrame")
        subcontainer.rowconfigure(0, weight=1)
        subcontainer.columnconfigure(0, weight=1, uniform="fred")
        subcontainer.columnconfigure(1, weight=1, uniform="fred")
        subcontainer.columnconfigure(2, weight=1, uniform="fred")
        subcontainer.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="wnes")
        decrementButton = ttk.Button(subcontainer, text="<", pad=(20, 5), style="Calibration.TButton")
        decrementButton.bind("<ButtonPress-1>", self.onDecrementBIASPressed)
        decrementButton.bind("<ButtonRelease-1>", self.onDecrementBIASReleased)
        decrementButton.grid(row=0, column=0, sticky="nes")
        biasLabel = ttk.Label(subcontainer, style="Value.Calibration.TLabel")
        biasLabel.grid(row=0, column=1, sticky="ns")
        incrementButton = ttk.Button(subcontainer, text=">", pad=(20, 5), style="Calibration.TButton")
        incrementButton.bind("<ButtonPress-1>", self.onIncrementBIASPressed)
        incrementButton.bind("<ButtonRelease-1>", self.onIncrementBIASReleased)
        incrementButton.grid(row=0, column=2, sticky="wns")
        self.filterValueLabels.insert(0, biasLabel)

    def createFilters(self):
        for idx, filter_ in enumerate(self.filters[::-1]):
            container = ttk.Frame(self.container, style="Calibration.TFrame")
            container.rowconfigure(0, weight=1)
            container.columnconfigure(0, weight=1)
            container.grid(row=idx, column=0, columnspan=4, padx=20, pady=5, sticky="wnes")
            self.createFilterAdjustmentContainer(container, len(self.filters) - idx - 1)
            ttk.Label(container, text=filter_, style="Label.Calibration.TLabel").grid(row=0, column=0, padx=(0, 5), pady=(0, 5), sticky="se")
            self.filterContainers.insert(0, container)
            self.disableFilter(0)

    def createForwardPower(self):
        ttk.Label(self.container, text="Forward Power:", style="Label.ValueDisplay.Calibration.TLabel").grid(row=6, column=0, padx=(0, 5), sticky="e")
        ttk.Label(self.container, textvariable=Data.getInstance().vars.P_F, style="Label.ValueDisplay.Calibration.TLabel").grid(row=6, column=1, padx=(5, 0), sticky="w")

    def createSaveButton(self):
        window_elements \
            .create_responding_menu_button(self.container, "Save", self.onSaveClicked) \
            .grid(row=6, column=2, sticky="se")

    def createCloseButton(self):
        ttk.Button(self.container, text="Close", pad=(40, 20), style="Settings.TButton", command=self.onCloseClicked) \
            .grid(row=6, column=3, sticky="se")

    def disableFilter(self, index):
        if index is None or index < 0 or index >= len(self.filterContainers):
            return
        [label.configure(text="") for label in self.filterValueLabels]
        filterContainer = self.filterContainers[index]
        self.recursiveEnableDisable(filterContainer, False)

    def recursiveEnableDisable(self, widget, enable):
        newState = [("!disabled" if enable else "disabled")]
        widget.state(newState)
        for child in widget.winfo_children():
            child.state(newState)
            self.recursiveEnableDisable(child, enable)

    def activateFilter(self, index):
        # Update the value label of the filter
        label = self.filterValueLabels[index]
        label.configure(text="{:.1f}".format(Data.getInstance().biasPercentage * 100))
        if index == self.activeFilter:
            return
        self.disableFilter(self.activeFilter)
        self.activeFilter = index
        filterContainer = self.filterContainers[index]
        self.recursiveEnableDisable(filterContainer, True)

    def onIncrementBIASPressed(self, _):
        self.incrementBIASEnabled = True
        self.onIncrementBIAS()

    def onIncrementBIASReleased(self, _):
        self.incrementBIASEnabled = False
        if self.incrementJob is None:
            return
        self.after_cancel(self.incrementJob)
        self.incrementJob = None

    def onIncrementBIAS(self):
        if not self.incrementBIASEnabled:
            return
        interface.increment_offset_BIAS()
        self.incrementJob = self.after(25, self.onIncrementBIAS)

    def onDecrementBIASPressed(self, _):
        self.decrementBIASEnabled = True
        self.onDecrementBIAS()

    def onDecrementBIASReleased(self, _):
        self.decrementBIASEnabled = False
        if self.decrementJob is None:
            return
        self.after_cancel(self.decrementJob)
        self.decrementJob = None

    def onDecrementBIAS(self):
        if not self.decrementBIASEnabled:
            return
        interface.decrement_offset_BIAS()
        self.decrementJob = self.after(25, self.onDecrementBIAS)

    def onSaveClicked(self):
        interface.store_config()

    def onCloseClicked(self):
        self.delegate.onCloseClicked()
