from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from canBus.canConnectorFactory import PowerSupplyDataSource, CanConnectorFactory
from config import Config

import interface
from data import Data
from menu import window_elements

HIGH_POWER = 'PE5 HIGH'
LOW_POWER = 'PE5 LOW'


class GeneralTab(ttk.Frame):

    def __init__(self, delegate, container):
        super().__init__(container)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.delegate = delegate

        self.container = ttk.Frame(self, pad=30)
        self.container.grid_propagate(False)
        self.container.grid(row=0, column=0, sticky="wnes")

        self.container.rowconfigure(4, weight=1)
        self.container.columnconfigure(0, weight=1, uniform="fred")
        self.container.columnconfigure(1, weight=1, uniform="fred")

        self.createDelayBetweenMeasurements()
        self.createCloseApplicationButton()
        self.createZeroFRAMButton()

        self.sixMeterStatus = interface.isTunerAtSixMeterEnabled()
        self.sixMeterStatusText = StringVar()
        self.createSixMeterBandSwitch()

        self.highLowPowerStatusEntry = None
        self.highLowPowerStatusText = StringVar()
        self.createHighLowPowerSwitch()

        self.createVoltageChange()

        self.createCloseButton()

    def createDelayBetweenMeasurements(self):
        container = ttk.Frame(self.container)
        container.grid(row=0, column=0, pady=5)
        ttk.Label(container, text="Delay Between Measurements").grid(row=0, column=0)
        ttk.Button(container, text="-", pad=(20, 0), style="Settings.TButton",
                   command=lambda: interface.decr_frq_count()).grid(row=0, column=1, padx=(30, 0))
        ttk.Label(container, textvariable=self.delegate.frqCountVar).grid(row=0, column=2)
        ttk.Button(container, text="+", pad=(20, 0), style="Settings.TButton",
                   command=lambda: interface.incr_frq_count()).grid(row=0, column=3)

    def createCloseApplicationButton(self):
        ttk.Button(self.container, text="Close Application", pad=(20, 20), style="Settings.TButton",
                   command=self.delegate.onCloseApplication).grid(row=1, column=0)

    def createZeroFRAMButton(self):
        window_elements.create_responding_menu_button(self.container, "Zero FRAM", self.onZeroFRAMClicked) \
            .grid(row=2, column=0)

    def createSixMeterBandSwitch(self):
        switchFrame = ttk.Frame(self.container)
        switchFrame.grid(row=3, column=0, pady=5)
        ttk.Label(switchFrame, text="Tuner at 6 m band").grid(row=0, column=0)
        self.sixMeterStatus = interface.isTunerAtSixMeterEnabled()
        self.sixMeterStatusText.set(self.getStatusText())
        ttk.Button(switchFrame, textvariable=self.sixMeterStatusText, pad=(80, 20), style="Settings.TButton",
                   command=self.onSixMeterSwitchClicked).grid(row=0, column=1, padx=(30, 0))

    def createHighLowPowerSwitch(self):
        switchFrame = ttk.Frame(self.container)
        switchFrame.grid(row=4, column=0, pady=5)
        ttk.Button(switchFrame, text="High/Low Power", pad=(30, 20), style="Settings.TButton",
                   command=self.onHighLowPowerClicked).grid(row=0, column=0, padx=(30, 0))
        self.highLowPowerStatusEntry = ttk.Entry(switchFrame, textvariable=self.highLowPowerStatusText,
                                                 state="readonly", width=10,
                                                 style='Status.TEntry', justify='center', font=("Lato", 24, "bold"),
                                                 validatecommand=self.is_undangerous_low_power)
        self.highLowPowerStatusEntry.grid(row=0, column=1)
        self.update_high_low_power_status()

    def update_high_low_power_status(self):
        if interface.getHighLowPower() == 1:
            self.highLowPowerStatusText.set(HIGH_POWER)
            Config.get_instance().isLowPower.set(False)
        else:
            self.highLowPowerStatusText.set(LOW_POWER)
            Config.get_instance().isLowPower.set(True)
        Config.get_instance().save_high_low_power()
        self.highLowPowerStatusEntry.validate()

    def is_undangerous_low_power(self):
        return self.highLowPowerStatusText.get() == LOW_POWER

    def onHighLowPowerClicked(self):
        if self.highLowPowerStatusText.get() == HIGH_POWER:
            interface.setHighLowPower(0)
        else:
            confirmed = messagebox.askokcancel(parent=self, title="Confirm PE5 high",
                                               message="Are you sure to set PE5 high? This can cause serious damage.",
                                               icon=messagebox.WARNING, default=messagebox.CANCEL)
            if confirmed:
                interface.setHighLowPower(1)
        self.update_high_low_power_status()

    def createVoltageChange(self):
        voltage_frame = ttk.Frame(self.container)

        voltage_frame.columnconfigure(0, weight=3, uniform="fred")
        voltage_frame.grid(row=0, column=1, pady=5)
        ttk.Label(voltage_frame, text="CAN voltage:").grid(row=0, column=0)
        if PowerSupplyDataSource(interface.get_power_supply_data_source()) == PowerSupplyDataSource.CAN:
            voltage_frame.columnconfigure(1, weight=1, uniform="fred")
            voltage_frame.columnconfigure(2, weight=1, uniform="fred")
            voltage_frame.columnconfigure(3, weight=1, uniform="fred")
            ttk.Button(voltage_frame, text="-", pad=(20, 0), style="Settings.TButton",
                       command=self.decreaseVoltage).grid(row=0, column=1, padx=(10, 0))
            ttk.Label(voltage_frame, textvariable=Data.getInstance().vars.voltage, anchor="e").grid(row=0, column=2)
            ttk.Button(voltage_frame, text="+", pad=(20, 0), style="Settings.TButton",
                       command=self.increaseVoltage).grid(row=0, column=3, padx=(10, 0))
        else:
            voltage_frame.columnconfigure(1, weight=3, uniform="fred")
            ttk.Label(voltage_frame, text="------------------").grid(row=0, column=1)

    def decreaseVoltage(self):
        self.changeVoltage(-0.1)

    def increaseVoltage(self):
        self.changeVoltage(0.1)

    def changeVoltage(self, change):
        new_voltage = Data.getInstance().voltage + change
        CanConnectorFactory.get_can_connector_instance().set_value([0x01, 0x00, 0x00, 0x00], new_voltage * 1024)

    def createCloseButton(self):
        ttk.Button(self.container, text="Close", pad=(40, 20), style="Settings.TButton", command=self.onCloseClicked) \
            .grid(row=5, column=1, sticky="se")

    def onCloseClicked(self):
        self.delegate.onCloseClicked()

    def onZeroFRAMClicked(self):
        interface.zeroFRAM()

    def onSixMeterSwitchClicked(self):
        interface.setTunerAtSixMeterEnabled(not self.sixMeterStatus)
        self.sixMeterStatus = interface.isTunerAtSixMeterEnabled()
        self.sixMeterStatusText.set(self.getStatusText())

    def getStatusText(self):
        if self.sixMeterStatus:
            return "ENABLED"
        return "DISABLED"
