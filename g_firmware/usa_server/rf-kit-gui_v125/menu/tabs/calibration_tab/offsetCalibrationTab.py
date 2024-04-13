from tkinter import *
from tkinter import ttk

from data import Data

import interface
from menu import window_elements


class OffsetCalibrationTab(ttk.Frame):

    filters = ["6m", "15/12/10m", "20/17m", "40/30m", "80/60m", "160m"]

    def __init__(self, delegate, container):
        super().__init__(container)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.delegate = delegate

        self.incrementFJob = None
        self.decrementFJob = None
        self.incrementRJob = None
        self.decrementRJob = None

        self.activeFilter = None
        self.filterContainers = list()
        self.filterValueLabels = list()

        self.container = ttk.Frame(self, pad=(30, 0, 30, 30))
        self.container.grid_propagate(False)
        self.container.grid(row=0, column=0, sticky="wnes")

        for i in range(1, 8):
            self.container.rowconfigure(i, weight=1, uniform="fred")
        self.container.columnconfigure(0, weight=1)

        self.createFilters()
        self.createSaveButton()
        self.createCloseButton()

    def createFilterAdjustmentContainer(self, container):
        subcontainer = ttk.Frame(container, style="Sub.Calibration.TFrame")
        subcontainer.rowconfigure(0, weight=1)
        subcontainer.columnconfigure(0, weight=1, uniform="fred")
        subcontainer.columnconfigure(1, weight=1, uniform="fred")
        subcontainer.columnconfigure(2, weight=1, uniform="fred")
        subcontainer.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="wnes")
        decrementButton = ttk.Button(subcontainer, text="<", pad=(20, 5), style="Calibration.TButton")
        decrementButton.bind("<ButtonPress-1>", self.onDecrementFPressed)
        decrementButton.bind("<ButtonRelease-1>", self.onDecrementFReleased)
        decrementButton.grid(row=0, column=0, sticky="nes")
        forwardLabel = ttk.Label(subcontainer, style="Value.Calibration.TLabel")
        forwardLabel.grid(row=0, column=1, sticky="ns")
        incrementButton = ttk.Button(subcontainer, text=">", pad=(20, 5), style="Calibration.TButton")
        incrementButton.bind("<ButtonPress-1>", self.onIncrementFPressed)
        incrementButton.bind("<ButtonRelease-1>", self.onIncrementFReleased)
        incrementButton.grid(row=0, column=2, sticky="wns")
        subcontainer = ttk.Frame(container, style="Sub.Calibration.TFrame")
        subcontainer.rowconfigure(0, weight=1)
        subcontainer.columnconfigure(0, weight=1, uniform="fred")
        subcontainer.columnconfigure(1, weight=1, uniform="fred")
        subcontainer.columnconfigure(2, weight=1, uniform="fred")
        subcontainer.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="wnes")
        decrementButton = ttk.Button(subcontainer, text="<", pad=(20, 5), style="Calibration.TButton")
        decrementButton.bind("<ButtonPress-1>", self.onDecrementRPressed)
        decrementButton.bind("<ButtonRelease-1>", self.onDecrementRReleased)
        decrementButton.grid(row=0, column=0, sticky="nes")
        reflectedLabel = ttk.Label(subcontainer, style="Value.Calibration.TLabel")
        reflectedLabel.grid(row=0, column=1, sticky="ns")
        incrementButton = ttk.Button(subcontainer, text=">", pad=(20, 5), style="Calibration.TButton")
        incrementButton.bind("<ButtonPress-1>", self.onIncrementRPressed)
        incrementButton.bind("<ButtonRelease-1>", self.onIncrementRReleased)
        incrementButton.grid(row=0, column=2, sticky="wns")
        self.filterValueLabels.insert(0, (forwardLabel, reflectedLabel))

    def createFilters(self):
        container = ttk.Frame(self.container)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1, uniform="fred")
        container.columnconfigure(1, weight=1, uniform="fred")
        container.grid(row=0, column=0, columnspan=3, padx=20, pady=(0, 5), sticky="wnes")
        ttk.Label(container, text="Forward", anchor="center", style="ColumnHeader.Calibration.TLabel").grid(row=0, column=0, sticky="wnes")
        ttk.Label(container, text="Reflected", anchor="center", style="ColumnHeader.Calibration.TLabel").grid(row=0, column=1, sticky="wnes")
        for idx, filter_ in enumerate(self.filters[::-1]):
            container = ttk.Frame(self.container, style="Calibration.TFrame")
            container.rowconfigure(0, weight=1)
            container.columnconfigure(0, weight=1, uniform="fred")
            container.columnconfigure(1, weight=1, uniform="fred")
            container.grid(row=idx + 1, column=0, columnspan=3, padx=20, pady=5, sticky="wnes")
            self.createFilterAdjustmentContainer(container)
            ttk.Label(container, text=filter_, style="Label.Calibration.TLabel").grid(row=0, column=1, padx=(0, 5), pady=(0, 5), sticky="se")
            self.filterContainers.insert(0, container)
            self.disableFilter(0)

    def createSaveButton(self):
        window_elements.create_responding_menu_button(self.container, "Save", self.onSaveClicked) \
            .grid(row=7, column=1, sticky="se")

    def createCloseButton(self):
        ttk.Button(self.container, text="Close", pad=(40, 20), style="Settings.TButton", command=self.onCloseClicked) \
            .grid(row=7, column=2, sticky="se")

    def disableFilter(self, index):
        if index is None or index < 0 or index >= len(self.filterContainers):
            return
        [label.configure(text="W") for label in self.filterValueLabels[index]]
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
        labelTuple = self.filterValueLabels[index]
        labelTuple[0].configure(text="{:.1f} W".format(Data.getInstance().P_F))
        labelTuple[1].configure(text="{:.1f} W".format(Data.getInstance().P_R))
        if index == self.activeFilter:
            return
        self.disableFilter(self.activeFilter)
        self.activeFilter = index
        filterContainer = self.filterContainers[index]
        self.recursiveEnableDisable(filterContainer, True)

    def onIncrementFPressed(self, _):
        self.incrementFEnabled = True
        self.onIncrementF()

    def onIncrementFReleased(self, _):
        self.incrementFEnabled = False
        if self.incrementFJob is None:
            return
        self.after_cancel(self.incrementFJob)
        self.incrementFJob = None

    def onIncrementF(self):
        if not self.incrementFEnabled:
            return
        interface.increment_offset_F()
        self.incrementFJob = self.after(25, self.onIncrementF)

    def onDecrementFPressed(self, _):
        self.decrementFEnabled = True
        self.onDecrementF()

    def onDecrementFReleased(self, _):
        self.decrementFEnabled = False
        if self.decrementFJob is None:
            return
        self.after_cancel(self.decrementFJob)
        self.decrementFJob = None

    def onDecrementF(self):
        if not self.decrementFEnabled:
            return
        interface.decrement_offset_F()
        self.decrementFJob = self.after(25, self.onDecrementF)

    def onIncrementRPressed(self, _):
        self.incrementREnabled = True
        self.onIncrementR()

    def onIncrementRReleased(self, _):
        self.incrementREnabled = False
        if self.incrementRJob is None:
            return
        self.after_cancel(self.incrementRJob)
        self.incrementRJob = None

    def onIncrementR(self):
        if not self.incrementREnabled:
            return
        interface.increment_offset_R()
        self.incrementRJob = self.after(25, self.onIncrementR)

    def onDecrementRPressed(self, _):
        self.decrementREnabled = True
        self.onDecrementR()

    def onDecrementRReleased(self, _):
        self.decrementREnabled = False
        if self.decrementRJob is None:
            return
        self.after_cancel(self.decrementRJob)
        self.decrementRJob = None

    def onDecrementR(self):
        if not self.decrementREnabled:
            return
        interface.decrement_offset_R()
        self.decrementRJob = self.after(25, self.onDecrementR)

    def onSaveClicked(self):
        interface.store_config()

    def onCloseClicked(self):
        self.delegate.onCloseClicked()
