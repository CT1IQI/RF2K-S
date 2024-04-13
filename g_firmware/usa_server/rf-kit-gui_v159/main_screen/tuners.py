from abc import ABC, abstractmethod
from enum import Enum
from tkinter import ttk, Canvas

from PIL import ImageTk, Image

from interface import InterfaceWrapper
from data import Data
from dimensions import DIMENSIONS
#from themes import logo


class TunerFrame(ttk.Frame, ABC):

    def __init__(self, container):
        super().__init__(container, borderwidth=4, relief="sunken")

    def grid(self, cnf={}, **kw):
        super().grid(cnf, **kw)
        # Call update_idletasks to make all geometry changes active so that winfo_width/height return correct values
        self.update_idletasks()
        self.after_grid_action()

    @abstractmethod
    def after_grid_action(self):
        pass

    def show(self):
        self.lift()

    def update_after_fetch_data(self):
        pass


logo = None


class NoTuner(TunerFrame):

    def __init__(self, container):
        super().__init__(container)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        global logo
        logo = ImageTk.PhotoImage(Image.open("resources/rf-kit_logo_black.png"))
        ttk.Label(self, image=logo).grid(row=0, column=0)

    def after_grid_action(self):
        pass


class Tuner(TunerFrame):

    class TunerType(Enum):

        AUTO = 0
        MANUAL = 1
        AUTO_TUNING = 2,
        AUTOTUNE_FROM_AUTO = 3

    class TunerSubType(Enum):

        CL = 0
        LC = 1
        BYPASS = 2

        def get_image_path(self):
            if self.value == 0:
                return "resources/CL.png"
            if self.value == 1:
                return "resources/LC.png"
            if self.value == 2:
                return "resources/Bypass.png"

    def __init__(self, delegate, container, tunerType, tunerSubType):
        if tunerType == Tuner.TunerType.MANUAL:
            if type(self) != ManualTuner:
                raise Exception("Type Manual only allowed for ManualTuner")
        super().__init__(container)
        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.delegate = delegate
        self.tunerType = tunerType
        self.tunerSubType = tunerSubType
        self.notTunedLabel = None
        self.atuBypassed = None
        self.inductance = None
        self.capacity = None

        self.flashStoreJob = None

        self.canvas = None
        self.tunerImage = None
        self.tunerImageOnCanvas = None

        self.modeButton = None
        self.adjustmentLabel = None
        self.frequencyTLabel = None
        self.bypassButton = None
        self.reset_tuner_button = None
        self.storeButton = None

        self.header = None
        self.create_header()
        self.create_canvas()
        self.create_footer()

    def get_mode_string(self):
        if self.tunerType == Tuner.TunerType.AUTO or self.tunerType == Tuner.TunerType.AUTOTUNE_FROM_AUTO:
            return "AUTO"
        else:
            return "MAN"

    def get_mode_button_style(self):
        if self.tunerType == Tuner.TunerType.AUTO or self.tunerType == Tuner.TunerType.AUTOTUNE_FROM_AUTO:
            return "Auto.Mode.Header.Tuner.TLabel"
        else:
            return "Manual.Mode.Header.Tuner.TLabel"

    def create_header(self):
        self.header = ttk.Frame(self)
        self.header.rowconfigure(0, weight=1, uniform="fred")
        self.header.rowconfigure(1, weight=1, uniform="fred")
        self.header.rowconfigure(2, weight=1, uniform="fred")
        self.header.columnconfigure(0, weight=1, uniform="fred")
        self.header.columnconfigure(1, weight=4, uniform="fred")
        self.header.columnconfigure(2, weight=1, uniform="fred")
        self.header.grid(row=0, column=0, columnspan=3, sticky="we")

        ttk.Label(self.header, textvariable=Data.getInstance().vars.segmentSize, anchor="center", style="Header.Tuner.TLabel").grid(row=0, column=1, sticky="we")
        self.adjustmentLabel = ttk.Label(self.header, anchor="center", style="Header.Tuner.TLabel")
        self.adjustmentLabel.grid(row=1, column=1, sticky="we")
        self.frequencyTLabel = ttk.Label(self.header, anchor="center", style="Header.Tuner.TLabel")
        self.frequencyTLabel.grid(row=2, column=1, sticky="we")
        if self.tunerType != Tuner.TunerType.MANUAL:
            self.adjustmentLabel.configure(text="Adjustment ok!")
            self.frequencyTLabel.configure(textvariable=Data.getInstance().vars.f_t)

        self.modeButton = ttk.Label(self.header, text=self.get_mode_string(), anchor="center", pad=(0, 15), style=self.get_mode_button_style())
        self.modeButton.bind("<ButtonRelease-1>", self.onModeClicked, True)
        self.modeButton.grid(row=0, column=2, rowspan=3, sticky="we")

    def create_canvas(self):
        self.canvas = Canvas(self, borderwidth=0, highlightthickness=0, bg="#000000", height=DIMENSIONS.TUNER_HEIGHT)
        self.canvas.grid(row=1, column=0, columnspan=3, pady=(20, 0), sticky="wnes")

    def create_footer(self):
        container = ttk.Frame(self, pad=(0, 2, 0, 0))
        container.columnconfigure(0, weight=1, uniform="fred")
        container.columnconfigure(1, weight=1, uniform="fred")
        container.columnconfigure(2, weight=1, uniform="fred")
        container.grid(row=2, column=0, columnspan=3, sticky="we")
        self.bypassButton = ttk.Label(container, text="Bypass", anchor="center", pad=(0, 5), style="Big.Button.Tuner.TLabel")
        self.bypassButton.bind("<ButtonRelease-1>", self.onBypassClicked, True)
        self.bypassButton.grid(row=0, column=0, sticky="wnes")
        self.reset_tuner_button = ttk.Label(container, text="Reset Tuner", anchor="center", justify="center", pad=(0, 5), style="Small.Button.Tuner.TLabel")
        self.reset_tuner_button.bind("<ButtonRelease-1>", self.onResetTunerClicked, True)
        self.reset_tuner_button.grid(row=0, column=1, padx=2, sticky="wnes")
        self.storeButton = ttk.Label(container, text="Store", anchor="center", pad=(0, 5), style="Big.Button.Tuner.TLabel")
        self.storeButton.bind("<ButtonRelease-1>", self.onStoreClicked, True)
        self.storeButton.grid(row=0, column=2, sticky="wnes")
        self.drawTuner()
        self.update_footer()

    def create_tuner_image(self):
        self.tunerImage = ImageTk.PhotoImage(Image.open(self.tunerSubType.get_image_path()).resize((self.canvas.winfo_width(),
                                                                                       self.canvas.winfo_height()),
                                                                                      Image.ANTIALIAS))
        if self.tunerImageOnCanvas is None:
            self.tunerImageOnCanvas = self.canvas.create_image(0, 0, image=self.tunerImage, anchor="nw")
        else:
            self.canvas.itemconfig(self.tunerImageOnCanvas, image=self.tunerImage)

    def getLMiddlePoint(self):
        if self.tunerType == Tuner.TunerType.AUTO:
            return 195, 37
        return (247, 42) if self.tunerSubType == Tuner.TunerSubType.CL else (144, 42)

    def getLAnchor(self):
        return "center"

    def getCMiddlePoint(self):
        if self.tunerType == Tuner.TunerType.AUTO:
            return (127, 65) if self.tunerSubType == Tuner.TunerSubType.CL else (265, 65)
        return (247, 112) if self.tunerSubType == Tuner.TunerSubType.CL else (144, 112)

    def getCAnchor(self):
        if self.tunerType == Tuner.TunerType.AUTO:
            return "nw" if self.tunerSubType == Tuner.TunerSubType.CL else "ne"
        return "center"

    decrementIncrementWidth = 40

    def getTextForValueAdjustButton(self, isIncrement, isSubtleAdjustment):
        character = ">" if isIncrement else "<"
        return character * (1 if isSubtleAdjustment else 2)

    def after_grid_action(self):
        self.create_tuner_image()

    def drawTuner(self):
        self.notTunedLabel = ttk.Label(self, text="Not Tuned", style="NotTuned.Tuner.TLabel")
        self.canvas.create_window((200, 66), anchor="center", window=self.notTunedLabel)

        if self.tunerSubType == Tuner.TunerSubType.BYPASS:
            if self.tunerType == Tuner.TunerType.AUTO:
                self.atuBypassed = ttk.Label(self, text="ATU bypassed")
                self.canvas.create_window((200, 66), anchor="center", window=self.atuBypassed)
        else:
            self.inductance = ttk.Label(self, textvariable=Data.getInstance().vars.L, style="Setting.Tuner.TLabel")
            self.canvas.create_window(self.getLMiddlePoint(), anchor=self.getLAnchor(), window=self.inductance)
            self.capacity = ttk.Label(self, textvariable=Data.getInstance().vars.C, style="Setting.Tuner.TLabel")
            self.canvas.create_window(self.getCMiddlePoint(), anchor=self.getCAnchor(), window=self.capacity)

    def update_after_fetch_data(self):
        self.update_footer()
        if Data.getInstance().errorState == Data.ErrorState.NOT_TUNED:
            self.update_for_not_tuned()
        else:
            self.update_for_tuned()

    def update_footer(self):
        if self.is_bypass_disabled():
            self.bypassButton.configure(style="Disabled.Big.Button.Tuner.TLabel")
        else:
            self.bypassButton.configure(style="Big.Button.Tuner.TLabel")

        if self.is_reset_tuner_disabled():
            self.reset_tuner_button.configure(style="Disabled.Small.Button.Tuner.TLabel")
        else:
            self.reset_tuner_button.configure(style="Small.Button.Tuner.TLabel")

        if self.flashStoreJob is None:
            if self.is_store_disabled():
                self.storeButton.configure(style="Disabled.Big.Button.Tuner.TLabel")
            else:
                self.storeButton.configure(style="Big.Button.Tuner.TLabel")

    def update_for_not_tuned(self):
        self.notTunedLabel.lift()
        self.adjustmentLabel.configure(style="Invisible.Header.Tuner.TLabel")
        self.frequencyTLabel.configure(style="Invisible.Header.Tuner.TLabel")
        if self.inductance:
            self.inductance.lower(self.canvas)
        if self.capacity:
            self.capacity.lower(self.canvas)
        if self.atuBypassed:
            self.atuBypassed.lower(self.canvas)

    def update_for_tuned(self):
        self.notTunedLabel.lower(self.canvas)
        if Data.getInstance().adjustment == 1:
            self.adjustmentLabel.configure(style="Header.Tuner.TLabel")
            self.frequencyTLabel.configure(style="Header.Tuner.TLabel")
        else:
            self.adjustmentLabel.configure(style="NeighborSegment.Header.Tuner.TLabel")
            self.frequencyTLabel.configure(style="NeighborSegment.Header.Tuner.TLabel")
        if self.inductance:
            self.inductance.lift()
        if self.capacity:
            self.capacity.lift()
        if self.atuBypassed:
            if Data.getInstance().tunerState == Data.TunerState.BYPASS:
                self.atuBypassed.lift()
            else:
                self.atuBypassed.lower(self.canvas)

    def onModeClicked(self, _):
        if Data.getInstance().inOperate and Data.getInstance().PTT:
            return
        self.delegate.onTunerModeClicked(self)

    def onBypassClicked(self, _):
        if self.is_bypass_disabled():
            return
        self.delegate.onBypassClicked(self)

    def is_bypass_disabled(self):
        return Data.getInstance().inOperate

    def onResetTunerClicked(self, _):
        if self.is_reset_tuner_disabled():
            return
        InterfaceWrapper.getInstance().reset_tuner()

    def is_reset_tuner_disabled(self):
        return Data.getInstance().tunerState != Data.TunerState.MANUAL or Data.getInstance().inOperate

    def onStoreClicked(self, _):
        if self.is_store_disabled():
            return
        InterfaceWrapper.getInstance().store_tuner()
        self.flashStoreButton()

    def is_store_disabled(self):
        return Data.getInstance().tunerState != Data.TunerState.MANUAL or Data.getInstance().inOperate

    def flashStoreButton(self, count=5):
        if self.flashStoreJob is not None:
            self.after_cancel(self.flashStoreJob)
            self.flashStoreJob = None
        newStyle = ("Big.Button.Tuner.TLabel" if (count % 2 == 0) else "Highlight.Big.Button.Tuner.TLabel")
        self.storeButton.configure(style=newStyle)
        if count > 0:
            count -= 1
            self.flashStoreJob = self.after(100, lambda: self.flashStoreButton(count))


class ManualTuner(Tuner):

    def __init__(self, delegate, container,  tunerSubType):
        self.manualTunerAdjustButtons = list()
        self.kButton = None
        super().__init__(delegate, container, Tuner.TunerType.MANUAL, tunerSubType)


    def create_header(self):
        super().create_header()
        if self.tunerSubType != Tuner.TunerSubType.BYPASS:
            self.kButton = ttk.Button(self.header, text="K", style="K.Header.Tuner.TButton", command=self.onKClicked)
            self.kButton.grid(row=0, column=0, rowspan=3, sticky="we")

    def drawTuner(self):
        super().drawTuner()
        if self.tunerSubType != Tuner.TunerSubType.BYPASS:
            # Decrease Inductance
            self.create_value_adjust_button(True, False, False)
            self.create_value_adjust_button(True, False, True)
            # Increase Inductance
            self.create_value_adjust_button(True, True, False)
            self.create_value_adjust_button(True, True, True)
            # Decrease Capacity
            self.create_value_adjust_button(False, False, False)
            self.create_value_adjust_button(False, False, True)
            # Increase Capacity
            self.create_value_adjust_button(False, True, False)
            self.create_value_adjust_button(False, True, True)

    def create_value_adjust_button(self, forInductance, isIncrement, isSubtleAdjustment):
        factor = 1 if isSubtleAdjustment else 10
        if isIncrement:
            if forInductance:
                change_value = lambda fixed_factor=factor: on_increment_l(fixed_factor)
            else:
                change_value = lambda fixed_factor=factor: on_increment_c(fixed_factor)
        else:
            if forInductance:
                change_value = lambda fixed_factor=factor: on_decrement_l(fixed_factor)
            else:
                change_value = lambda fixed_factor=factor: on_decrement_c(fixed_factor)
        button = ttk.Button(self, text=self.getTextForValueAdjustButton(isIncrement, isSubtleAdjustment), pad=(15, 9),
                            command=change_value, style="Adjust.Tuner.TButton")

        coordinates = self.getLMiddlePoint() if forInductance else self.getCMiddlePoint()
        coordinateAdjustment = 62 if isSubtleAdjustment else 118
        coordinates = (coordinates[0] + (coordinateAdjustment if isIncrement else -coordinateAdjustment), coordinates[1])
        self.manualTunerAdjustButtons.append(button)
        self.canvas.create_window(coordinates, window=button)

    def update_after_fetch_data(self):
        super().update_after_fetch_data()
        if is_manual_tuning_allowed():
            new_state = '!disabled'
        else:
            new_state = 'disabled'
        for button in self.manualTunerAdjustButtons:
            button.configure(state=new_state)
        if self.kButton is not None:
            self.kButton.configure(state=new_state)

    def update_for_not_tuned(self):
        super().update_for_not_tuned()
        for button in self.manualTunerAdjustButtons:
            button.lower(self.canvas)

    def update_for_tuned(self):
        super().update_for_tuned()
        for button in self.manualTunerAdjustButtons:
            button.lift()

    def onKClicked(self):
        if is_manual_tuning_allowed():
            self.delegate.onKClicked(self)


def on_decrement_l(factor):
    if is_manual_tuning_allowed():
        InterfaceWrapper.getInstance().decrement_L(factor)


def on_increment_l(factor):
    if is_manual_tuning_allowed():
        InterfaceWrapper.getInstance().increment_L(factor)


def on_decrement_c(factor):
    if is_manual_tuning_allowed():
        InterfaceWrapper.getInstance().decrement_C(factor)


def on_increment_c(factor):
    if is_manual_tuning_allowed():
        InterfaceWrapper.getInstance().increment_C(factor)


def is_manual_tuning_allowed():
    if Data.getInstance().tunerState != Data.TunerState.MANUAL:
        return False
    if Data.getInstance().inOperate and Data.getInstance().PTT:
        return False
    if Data.getInstance().P_F > 30:
        return False
    return True
