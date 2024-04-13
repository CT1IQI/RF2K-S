import timeit
from abc import ABC, abstractmethod
from tkinter import ttk, StringVar

from PIL import Image, ImageTk

from config import Config
from interface import InterfaceWrapper
from canBus.canConnectorFactory import CanConnectorFactory
from data import Data


class OperatingButton(ttk.Label, ABC):

    def __init__(self, container, text=None, textvariable=None, imageName=None, side=None, **kwargs):
        super().__init__(container, text=text, textvariable=textvariable, compound="top", **kwargs)

        if imageName is not None and side is not None:
            img = Image.open(imageName)
            img = img.resize((side, side), Image.ANTIALIAS)
            self.curImage = ImageTk.PhotoImage(img)
            self.configure(image=self.curImage)
        Data.getInstance().register_fetch_watcher(self.update_after_fetch_data)

    def destroy(self):
        Data.getInstance().unregister_fetch_watcher(self.update_after_fetch_data)
        super().destroy()

    @abstractmethod
    def update_after_fetch_data(self):
        pass


class TuneButton(OperatingButton):
    def __init__(self, container):
        self.label = StringVar(value="Tune")
        super().__init__(container, textvariable=self.label, style="Off.Tunemode.OperatingButton.TLabel")
        self.bind("<ButtonRelease-1>", self.onAutotuneClicked)
        self.isEnabled = True

    def onAutotuneClicked(self, _):
        if not self.isEnabled:
            return
        if Data.getInstance().inOperate and Data.getInstance().PTT:
            return

        InterfaceWrapper.getInstance().autotune()
        Data.getInstance().fetch_data_once()

    def update_after_fetch_data(self):
        if Data.getInstance().tunerState is Data.TunerState.AUTO or Data.getInstance().tunerState is Data.TunerState.AUTO_TUNING_FROM_AUTO:
            self.label.set("Tune & Store")
        else:
            self.label.set("Tune")

        if Data.getInstance().tunerState is Data.TunerState.AUTO_TUNING or Data.getInstance().tunerState is Data.TunerState.AUTO_TUNING_FROM_AUTO:
            self.isEnabled = False
            new_style = "On.Tunemode.OperatingButton.TLabel"
        elif Data.getInstance().tunerState is not Data.TunerState.MANUAL and Data.getInstance().tunerState is not Data.TunerState.AUTO:
            self.isEnabled = False
            new_style = "Disabled.Tunemode.OperatingButton.TLabel"
        elif Data.getInstance().inOperate or Data.getInstance().P_F < self.minimum_tune_power() or Data.getInstance().P_F > 30.:
            self.isEnabled = False
            new_style = "Disabled.Tunemode.OperatingButton.TLabel"
        else:
            self.isEnabled = True
            new_style = "Off.Tunemode.OperatingButton.TLabel"
        self.configure(style=new_style)

    def minimum_tune_power(self):
        if Config.get_instance().transceiverCanSetPowerForAutotuneVar.get():
            return 0.
        else:
            return 3.


class ResetButton(OperatingButton):
    def __init__(self, container, large=False):
        self.onStyle = "On.Reset.Large.OperatingButton.TLabel" if large else "On.Reset.OperatingButton.TLabel"
        self.offStyle = "Off.Reset.Large.OperatingButton.TLabel" if large else "Off.Reset.OperatingButton.TLabel"
        super().__init__(container, "Reset", style=self.offStyle)
        self.bind("<ButtonRelease-1>", self.onResetClicked)
        self.flashResetJob = None
        self.isEnabled = True

    def onResetClicked(self, _=None):
        if not self.isEnabled:
            return False
        if Data.getInstance().inOperate and Data.getInstance().PTT:
            return False
        InterfaceWrapper.getInstance().reset_error_state()
        self.after(5000, CanConnectorFactory.get_can_connector_instance().initialize_power_supply)
        self.flashResetButton()
        return True

    def flashResetButton(self, count=5):
        if self.flashResetJob is not None:
            self.after_cancel(self.flashResetJob)
            self.flashResetJob = None
        new_style = (self.offStyle if (count % 2 == 0) else self.onStyle)
        self.configure(style=new_style)
        if count > 0:
            count -= 1
            self.flashResetJob = self.after(300, lambda: self.flashResetButton(count))

    def update_after_fetch_data(self):
        if Data.getInstance().tunerState is not Data.TunerState.AUTO_TUNING:
            self.isEnabled = True
        else:
            self.isEnabled = False

        if Data.getInstance().vars.status.get():  # error message visible
            self.state(['alternate'])
        else:
            self.state(['!alternate'])


class OperateStandbyButton(OperatingButton):
    def __init__(self, container, large=False):
        self.operateStyle = "Operate.Large.OperatingButton.TLabel" if large else "Operate.OperatingButton.TLabel"
        self.standbyStyle = "Standby.Large.OperatingButton.TLabel" if large else "Standby.OperatingButton.TLabel"
        super().__init__(container, "Standby", style=self.standbyStyle)
        self.bind("<ButtonRelease-1>", self.onStandbyOperateClicked)
        self.isEnabled = True

    def onStandbyOperateClicked(self, _=None, to_operate=None):
        if not self.isEnabled:
            return False
        if Data.getInstance().PTT:
            return False
        if Data.getInstance().inOperate:
            if to_operate is None or not to_operate:
                self.onSetToStandby()
        else:
            if to_operate is None or to_operate:
                self.onSetToOperate()
        return True

    def onSetToOperate(self):
        InterfaceWrapper.getInstance().set_operate()

    def onSetToStandby(self):
        InterfaceWrapper.getInstance().set_standby()

    def update_after_fetch_data(self):
        if Data.getInstance().tunerState is not Data.TunerState.AUTO_TUNING:
            self.isEnabled = True if Data.getInstance().errorState == Data.ErrorState.NONE or Data.getInstance().errorState == Data.ErrorState.NOT_TUNED else False
        else:
            self.isEnabled = False

        if Data.getInstance().inOperate:
            self.configure(style=self.operateStyle, text="Operate")
        else:
            self.configure(style=self.standbyStyle, text="Standby")


class OperatingButtons(ttk.Frame):

    def __init__(self, container, contest=False):
        super().__init__(container)

        if not contest:
            self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        if not contest:
            self.tune = TuneButton(self)
            self.tune.grid(row=0, column=0)
        self.reset = ResetButton(self, contest)
        self.reset.grid(row=0, column=1, sticky="n")
        self.standbyOperate = OperateStandbyButton(self, contest)
        self.standbyOperate.grid(row=0, column=2)
