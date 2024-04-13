from tkinter import *
from tkinter import ttk

from interface import InterfaceWrapper
from debug.debugCalibrationEnums import Band, DebugCalibrationType


class DebugCalibrationTab(ttk.Frame):

    filters = [[Band.BAND_6_M, Band.BAND_10_M, Band.BAND_12_M, Band.BAND_15_M, Band.BAND_17_M, Band.BAND_20_M],
               [Band.BAND_30_M, Band.BAND_40_M, Band.BAND_60_M, Band.BAND_80_M, Band.BAND_160_M]]

    def __init__(self, delegate, container, debug_calibration_type: DebugCalibrationType):
        super().__init__(container)

        self.debugCalibrationType = debug_calibration_type
        self.digitsVarsByFilter = dict()

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.delegate = delegate

        self.incrementJobs = dict()
        self.decrementJobs = dict()

        self.container = ttk.Frame(self, pad=(30, 0, 30, 30))
        self.container.grid_propagate(False)
        self.container.grid(row=0, column=0, sticky="wnes")

        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.createFilters()

        bottom_container = ttk.Frame(self.container)
        bottom_container.grid(row=1, column=0, sticky="wnes")
        bottom_container.rowconfigure(1, weight=1)
        bottom_container.columnconfigure(2, weight=1)
    #    self.createForwardPower(bottom_container)
        self.createCloseButton(bottom_container)

    def createFilterAdjustmentContainer(self, container, filter_key: Band):
        subcontainer = ttk.Frame(container, style="Sub.Calibration.TFrame")
        subcontainer.rowconfigure(0, weight=1)
        subcontainer.columnconfigure(0, weight=1, uniform="fred")
        subcontainer.columnconfigure(1, weight=1, uniform="fred")
        subcontainer.columnconfigure(2, weight=1, uniform="fred")
        subcontainer.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="wnes")
        decrementButton = ttk.Button(subcontainer, text="<", pad=(20, 5), style="Calibration.TButton")
        decrementButton.bind("<ButtonPress-1>", lambda x: self.on_decrement_digits_pressed(filter_key))
        decrementButton.bind("<ButtonRelease-1>", lambda x: self.on_decrement_digits_released(filter_key))
        decrementButton.grid(row=0, column=0, sticky="nes")
        digits_var = IntVar()
        digits_label = ttk.Label(subcontainer, textvariable=digits_var, style="Value.Calibration.TLabel")
        digits_label.grid(row=0, column=1, sticky="ns")
        incrementButton = ttk.Button(subcontainer, text=">", pad=(20, 5), style="Calibration.TButton")
        incrementButton.bind("<ButtonPress-1>", lambda x: self.on_increment_digits_pressed(filter_key))
        incrementButton.bind("<ButtonRelease-1>", lambda x: self.on_increment_digits_released(filter_key))
        incrementButton.grid(row=0, column=2, sticky="wns")
        self.digitsVarsByFilter[filter_key] = digits_var

    def createFilters(self):
        filter_container = ttk.Frame(self.container)
        filter_container.grid(row=0, column=0, sticky="wnes")
        filter_container.columnconfigure(1, weight=1)
        filter_container.columnconfigure(5, weight=1)
        for i in range(0, 6):
            filter_container.rowconfigure(i, weight=1, uniform="fred")
        for idx, column in enumerate(self.filters):
            for idy, filter_ in enumerate(column):
                container = ttk.Frame(filter_container, style="Calibration.TFrame")
                container.rowconfigure(0, weight=1)
                container.columnconfigure(0, weight=1)
                container.grid(row=idy, column=idx*4, columnspan=4, padx=20, pady=5, sticky="wnes")
                self.createFilterAdjustmentContainer(container, filter_)
                ttk.Label(container, text=filter_.displayName, style="Label.Calibration.TLabel").grid(row=0, column=0, padx=(0, 5), pady=(0, 5), sticky="se")

    def createCloseButton(self, bottom_container):
        ttk.Button(bottom_container, text="Close", pad=(40, 20), style="Settings.TButton", command=self.onCloseClicked) \
            .grid(row=1, column=3, sticky="se")

    def update_all_digits(self):
        for filter_key, digits_var in self.digitsVarsByFilter.items():
            self.update_digit(filter_key, digits_var)

    def update_digit(self, filter_key: Band, digits_var: IntVar = None):
        if digits_var is None:
            digits_var = self.digitsVarsByFilter[filter_key]
        current_digits = InterfaceWrapper.getInstance().get_dac_offset(self.debugCalibrationType, filter_key)
        digits_var.set(current_digits)

    def on_increment_digits_pressed(self, filter_key):
        self.keep_incrementing_dac(filter_key)

    def on_increment_digits_released(self, filter_key):
        if self.incrementJobs[filter_key] is None:
            return
        self.after_cancel(self.incrementJobs[filter_key])
        self.incrementJobs[filter_key] = None

    def keep_incrementing_dac(self, filter_key):
        InterfaceWrapper.getInstance().increment_dac_offset(self.debugCalibrationType, filter_key)
        self.incrementJobs[filter_key] = self.after(25, lambda: self.keep_incrementing_dac(filter_key))
        self.update_digit(filter_key)

    def on_decrement_digits_pressed(self, filter_key):
        self.keep_decrementing_dac(filter_key)

    def on_decrement_digits_released(self, filter_key):
        if self.decrementJobs[filter_key] is None:
            return
        self.after_cancel(self.decrementJobs[filter_key])
        self.decrementJobs[filter_key] = None

    def keep_decrementing_dac(self, filter_key):
        InterfaceWrapper.getInstance().decrement_dac_offset(self.debugCalibrationType, filter_key)
        self.decrementJobs[filter_key] = self.after(25, lambda: self.keep_decrementing_dac(filter_key))
        self.update_digit(filter_key)

    def onCloseClicked(self):
        self.delegate.onCloseClicked()
