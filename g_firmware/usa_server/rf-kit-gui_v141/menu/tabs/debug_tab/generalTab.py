from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from canBus.canConnectorFactory import PowerSupplyDataSource, CanConnectorFactory
from config import Config

from interface import InterfaceWrapper
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
        self.createCloseApplicationAndZeroFRAMButtons()

        self.sixMeterStatus = InterfaceWrapper.getInstance().isTunerAtSixMeterEnabled()
        self.sixMeterStatusText = StringVar()
        self.createSixMeterBandSwitch()

        self.highLowPowerStatusEntry = None
        self.highLowPowerStatusText = StringVar()
        self.createHighLowPowerSwitch()

        self.nominalVoltageVar = StringVar(value="{:.1f} V".format(Config.get_instance().canPower["voltage"]))
        self.createVoltageChange()

        self.createAutotuneThresholdChange()

        self.createCloseButton()

    def createDelayBetweenMeasurements(self):
        container = ttk.Frame(self.container)
        container.grid(row=0, column=0, pady=5)
        ttk.Label(container, text="Delay Between Measurements").grid(row=0, column=0)
        ttk.Button(container, text="-", pad=(20, 0), style="Settings.TButton",
                   command=lambda: InterfaceWrapper.getInstance().decr_frq_count()).grid(row=0, column=1, padx=(30, 0))
        ttk.Label(container, textvariable=self.delegate.frqCountVar).grid(row=0, column=2)
        ttk.Button(container, text="+", pad=(20, 0), style="Settings.TButton",
                   command=lambda: InterfaceWrapper.getInstance().incr_frq_count()).grid(row=0, column=3)

    def createCloseApplicationAndZeroFRAMButtons(self):
        container = ttk.Frame(self.container)
        container.grid(row=1, column=0, pady=5)
        ttk.Button(container, text="Close Application", pad=(20, 20), style="Settings.TButton",
                   command=self.delegate.onCloseApplication).grid(row=0, column=0)
        window_elements.create_responding_menu_button(container, "Zero FRAM", self.onZeroFRAMClicked) \
            .grid(row=0, column=1)

    def createSixMeterBandSwitch(self):
        switchFrame = ttk.Frame(self.container)
        switchFrame.grid(row=2, column=0, pady=5)
        ttk.Label(switchFrame, text="Tuner at 6 m band").grid(row=0, column=0)
        self.sixMeterStatus = InterfaceWrapper.getInstance().isTunerAtSixMeterEnabled()
        self.sixMeterStatusText.set(self.getStatusText())
        ttk.Button(switchFrame, textvariable=self.sixMeterStatusText, pad=(80, 20), style="Settings.TButton",
                   command=self.onSixMeterSwitchClicked).grid(row=0, column=1, padx=(30, 0))

    def createHighLowPowerSwitch(self):
        switchFrame = ttk.Frame(self.container)
        switchFrame.grid(row=3, column=0, pady=5)
        ttk.Button(switchFrame, text="High/Low Power", pad=(30, 20), style="Settings.TButton",
                   command=self.onHighLowPowerClicked).grid(row=0, column=0, padx=(30, 0))
        self.highLowPowerStatusEntry = ttk.Entry(switchFrame, textvariable=self.highLowPowerStatusText,
                                                 state="readonly", width=10,
                                                 style='Status.TEntry', justify='center', font=("Lato", 24, "bold"),
                                                 validatecommand=self.is_undangerous_low_power)
        self.highLowPowerStatusEntry.grid(row=0, column=1)
        self.update_high_low_power_status()

    def update_high_low_power_status(self):
        if InterfaceWrapper.getInstance().getHighLowPower() == 1:
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
            InterfaceWrapper.getInstance().setHighLowPower(0)
        else:
            confirmed = messagebox.askokcancel(parent=self, title="Confirm PE5 high",
                                               message="Are you sure to set PE5 high? This can cause serious damage.",
                                               icon=messagebox.WARNING, default=messagebox.CANCEL)
            if confirmed:
                InterfaceWrapper.getInstance().setHighLowPower(1)
        self.update_high_low_power_status()

    def createVoltageChange(self):
        voltage_frame = ttk.Frame(self.container)

        voltage_frame.columnconfigure(0, weight=3, uniform="fred")
        voltage_frame.grid(row=0, column=1, pady=5)
        ttk.Label(voltage_frame, text="CAN voltage:").grid(row=0, column=0)
        ttk.Label(voltage_frame, textvariable=Data.getInstance().vars.voltage, anchor="e").grid(row=0, column=1)
        ttk.Label(voltage_frame, text="CAN nominal voltage:").grid(row=1, column=0)
        power_supply_data_source = PowerSupplyDataSource(InterfaceWrapper.getInstance().get_power_supply_data_source())
        voltage_frame.columnconfigure(1, weight=3, uniform="fred")
        voltage_setter_frame = ttk.Frame(voltage_frame)
        voltage_setter_frame.grid(row=1, column=1)
        if power_supply_data_source == PowerSupplyDataSource.CAN or power_supply_data_source == PowerSupplyDataSource.CAN_FROM_CONTROLLER:
            voltage_setter_frame.columnconfigure(0, weight=1, uniform="fred")
            voltage_setter_frame.columnconfigure(1, weight=1, uniform="fred")
            voltage_setter_frame.columnconfigure(2, weight=1, uniform="fred")
            ttk.Button(voltage_setter_frame, text="-", pad=(20, 0), style="Settings.TButton",
                       command=self.decreaseVoltage).grid(row=0, column=0, padx=(10, 0))
            ttk.Label(voltage_setter_frame, textvariable=self.nominalVoltageVar, anchor="e").grid(row=0, column=1)
            ttk.Button(voltage_setter_frame, text="+", pad=(20, 0), style="Settings.TButton",
                       command=self.increaseVoltage).grid(row=0, column=2, padx=(10, 0))
        else:
            voltage_setter_frame.columnconfigure(0, weight=3, uniform="fred")
            ttk.Label(voltage_frame, text="------------------").grid(row=0, column=1)

    def decreaseVoltage(self):
        self.changeVoltage(-0.5)

    def increaseVoltage(self):
        self.changeVoltage(0.5)

    def changeVoltage(self, change):
        new_voltage = Config.get_instance().canPower["voltage"] + change
        Config.get_instance().canPower["voltage"] = new_voltage
        Config.get_instance().save_can_power()
        self.nominalVoltageVar.set("{:.1f} V".format(new_voltage))
        CanConnectorFactory.get_can_connector_instance().set_nominal_voltage(new_voltage)

    def createAutotuneThresholdChange(self):
        autotune_frame = ttk.Frame(self.container)

        autotune_frame.columnconfigure(0, weight=3, uniform="fred")
        autotune_frame.grid(row=1, column=1, pady=5)
        ttk.Label(autotune_frame, text="Autotune return loss threshold:").grid(row=0, column=0)
        threshold_frame = ttk.Frame(autotune_frame)
        threshold_frame.grid(row=0, column=1)
        threshold_frame.columnconfigure(0, weight=1, uniform="fred")
        threshold_frame.columnconfigure(1, weight=1, uniform="fred")
        threshold_frame.columnconfigure(2, weight=1, uniform="fred")
        ttk.Button(threshold_frame, text="-", pad=(20, 0), style="Settings.TButton",
                   command=self.decreaseAutotuneThreshold).grid(row=0, column=0, padx=(10, 0))
        ttk.Label(threshold_frame, textvariable=Data.getInstance().vars.autotune_return_loss_threshold_var, anchor="e").grid(row=0, column=1)
        ttk.Button(threshold_frame, text="+", pad=(20, 0), style="Settings.TButton",
                   command=self.increaseAutotuneThreshold).grid(row=0, column=2, padx=(10, 0))

    def decreaseAutotuneThreshold(self):
        self.changeAutotuneThreshold(-0.2)

    def increaseAutotuneThreshold(self):
        self.changeAutotuneThreshold(0.2)

    def changeAutotuneThreshold(self, change):
        new_threshold = Data.getInstance().autotune_return_loss_threshold + change
        InterfaceWrapper.getInstance().set_autotune_return_loss_threshold(new_threshold)

    def createCloseButton(self):
        ttk.Button(self.container, text="Close", pad=(40, 20), style="Settings.TButton", command=self.onCloseClicked) \
            .grid(row=5, column=1, sticky="se")

    def onCloseClicked(self):
        self.delegate.onCloseClicked()

    def onZeroFRAMClicked(self):
        InterfaceWrapper.getInstance().zeroFRAM()

    def onSixMeterSwitchClicked(self):
        InterfaceWrapper.getInstance().setTunerAtSixMeterEnabled(not self.sixMeterStatus)
        self.sixMeterStatus = InterfaceWrapper.getInstance().isTunerAtSixMeterEnabled()
        self.sixMeterStatusText.set(self.getStatusText())

    def getStatusText(self):
        if self.sixMeterStatus:
            return "ENABLED"
        return "DISABLED"
