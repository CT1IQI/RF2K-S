from tkinter import ttk, IntVar, BooleanVar, StringVar
from tkinter import messagebox

from contestDisplay import ContestDisplay
from data import Data, BANDS
from config import Config
from displaySetting import DisplaySetting
from keyboard.keyboard import Keyboard
from cursorSetting import CursorSetting

from interface import InterfaceWrapper
from mainScreenTypeSetting import MainScreenType, MainScreenTypeSetting
from menu import window_elements
from menu.lazyNotebook import LazyNotebook
from sleepTimer import SleepTimer


class TunerOnOffSettings(ttk.Frame):

    def __init__(self, container, **kwargs):
        super().__init__(container, **kwargs)
        self.tunerOnBooleans = list()
        self.initialize_tuner_on_off_booleans()

        for row in range(0, 4):
            self.rowconfigure(row, weight=1, uniform="fred")
        for column in range(0, 3):
            self.columnconfigure(column, weight=1, uniform="fred")
        self.columnconfigure(0, weight=1, uniform="pad")
        self.columnconfigure(4, weight=1, uniform="pad")
        self.grid(row=0, column=0, sticky="we")

        for (index, band) in enumerate(BANDS):
            tuner_on_for_band = self.tunerOnBooleans[index]
            window_elements.create_check_button_with_text(self, text=band, variable=tuner_on_for_band,
                                                          style="Radiobuttonlike.TCheckbutton",
                                                          command=lambda band_idx=index: self.set_tuner_on_off(band_idx))\
                .grid(row=index % 4, column=int(index/4)+1, sticky="w", padx=10)

    def initialize_tuner_on_off_booleans(self):
        for on_off in InterfaceWrapper.getInstance().get_tuner_on_off_per_band():
            self.tunerOnBooleans.append(BooleanVar(value=bool(on_off)))

    def refresh_tuner_on_off_booleans(self):
        for (index, on_off) in enumerate(InterfaceWrapper.getInstance().get_tuner_on_off_per_band()):
            self.tunerOnBooleans[index].set(bool(on_off))

    def set_tuner_on_off(self, band_index):
        InterfaceWrapper.getInstance().set_tuner_on_off_for_band(band_index, int(self.tunerOnBooleans[band_index].get()))


class TunerStorageSettings(ttk.Frame):

    def __init__(self, container, current_bank, **kwargs):
        super().__init__(container, **kwargs)
        self.currentBank = IntVar(value=current_bank)
        self.currentExtAntenna = Data.getInstance().vars.curExtAntennaNumberString

        self.extAntennaWidgets = list()

        for i in range(1, 4):
            self.rowconfigure(i, weight=1, uniform="fred")

        self.columnconfigure(2, weight=4)


        self.create_headers()
        self.create_bank_selection()
        self.create_antennas()


    def create_headers(self):
        ttk.Label(self, text="Memory Bank").grid(row=0, column=0, columnspan=2)
        ttk.Label(self, text="Antenna").grid(row=0, column=3, columnspan=4)

    def create_bank_selection(self):
        for i in range(3):
            window_elements.create_radio_button_with_text(self, text=(i + 1), compound="right",
                                                          variable=self.currentBank, value=i,
                                                          command=self.on_memory_bank_selected).grid(row=i+1,
                                                                                                     column=0, padx=(40, 0))
            ttk.Button(self, style="Trash.Settings.TButton",
                       # parameter in lambda has to be bound
                       command=lambda bound_memory_to_delete_idx=i: self.show_bank_delete_confirmation(
                           bound_memory_to_delete_idx)) \
                .grid(row=i+1, column=1, padx=40, sticky="w")

    def show_bank_delete_confirmation(self, index):
        result = messagebox.askokcancel(parent=self, title="Delete Memory Bank",
                                        message="Are you sure you want to delete the memory bank " + str(index + 1) + "?")
        if result:
            InterfaceWrapper.getInstance().delete_storage(index)

    def on_memory_bank_selected(self):
        InterfaceWrapper.getInstance().set_storage_bank(self.currentBank.get())

    def create_antennas(self):
        for i in range(4):
            row = (i % 2) + 1
            column_offset = int(i / 2) * 2 + 3
            ttk.Label(self, style="VeryHuge.TLabel", text=(i + 1)).grid(row=row, column=column_offset, sticky="e")
            ttk.Button(self, style="Trash.Settings.TButton",
                       command=lambda i=i: self.show_antenna_delete_confirmation(i)).grid(row=row, column=column_offset+1, padx=(20,40), sticky="w")
        ext_ant_label_container = ttk.Frame(self)
        ext_ant_label_container.grid(row=3, column=2, columnspan=4, sticky="e")
        static_ext_label = ttk.Label(ext_ant_label_container, style="Disableble.VeryHuge.TLabel", text="Ext. Ant.")
        static_ext_label.grid(row=0, column=0)
        self.extAntennaWidgets.append(static_ext_label)
        var_ext_label = ttk.Label(ext_ant_label_container, style="Disableble.VeryHuge.TLabel", textvariable=self.currentExtAntenna)
        var_ext_label.grid(row=0, column=1)
        self.extAntennaWidgets.append(var_ext_label)
        ext_button = ttk.Button(self, style="Trash.Settings.TButton",
                       command=lambda: self.show_ext_antenna_delete_confirmation())
        ext_button.grid(row=3, column=6, padx=(20, 40), sticky="w")
        self.extAntennaWidgets.append(ext_button)

        self.update_ext_antenna_state()

    def update_ext_antenna_state(self):
        print("update_ext_antenna_state")
        for widget in self.extAntennaWidgets:
            if Data.getInstance().useExternalAntenna:
                widget.state(['!disabled'])
            else:
                widget.state(['disabled'])


    def show_antenna_delete_confirmation(self, index):
        result = messagebox.askokcancel(parent=self, title="Delete Tuner Antenna",
                                        message="Are you sure you want to delete the tuner antenna " + str(index+1) + "?")
        if result:
            InterfaceWrapper.getInstance().delete_tuner_antenna(index)

    def show_ext_antenna_delete_confirmation(self):
        if not Data.getInstance().useExternalAntenna:
            return
        index = Data.getInstance().curAntenna
        result = messagebox.askokcancel(parent=self, title="Delete Tuner Antenna",
                                        message="Are you sure you want to delete the external tuner antenna " + str(index+1) + "?")
        if result:
            InterfaceWrapper.getInstance().delete_tuner_ext_antenna(index)


class GeneralSettings(ttk.Frame):


    def __init__(self, container):
        super().__init__(container)

        for i in range(0, 5):
            self.rowconfigure(i, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)

        ttk.Label(self, text="Display").grid(row=0, column=0, sticky="e")
        self.displayButton = ttk.Button(self, textvariable=DisplaySetting.get_instance().displayState, pad=(20, 10), style="OnOff.Settings.TButton",
                   command=self.on_display_button_clicked)
        self.displayButton.grid(row=0, column=1, padx=30, sticky="we")
        self.updateDisplayButtonState()

        ttk.Label(self, text="Cursor").grid(row=1, column=0, sticky="e")
        ttk.Button(self, text="ON / OFF", pad=(20, 10), style="Settings.TButton",
                   command=self.on_cursor_button_clicked).grid(row=1, column=1, padx=30, sticky="we")

        ttk.Label(self, text="Type").grid(row=2, column=0, sticky="e")
        ttk.Button(self, textvariable=MainScreenTypeSetting.get_instance().currentMainScreenStringVar, pad=(20, 10), style="Settings.TButton",
                   command=self.on_display_type_button_clicked).grid(row=2, column=1, padx=30, sticky="we")


        ttk.Label(self, text="Sleep Timer").grid(row=3, column=0, sticky="e")
        self.sleepButton = ttk.Button(self, textvariable=SleepTimer.get_instance().stateString, pad=(20, 10),
                                      style="OnOff.Settings.TButton", command=self.on_sleep_timer_button_clicked)
        self.updateSleepButtonState()
        self.sleepButton.grid(row=3, column=1, padx=30, sticky="we")
        timerAdjustmentContainer = ttk.Frame(self)
        timerAdjustmentContainer.columnconfigure(0, weight=1)
        timerAdjustmentContainer.columnconfigure(3, weight=1)
        timerAdjustmentContainer.grid(row=4, column=1, sticky="we")
        ttk.Button(timerAdjustmentContainer, text="<", pad=(20, 5), style="Settings.TButton",
                   command=SleepTimer.get_instance().decrement_minutes).grid(row=0, column=0, sticky="e", padx=10)
        ttk.Label(timerAdjustmentContainer, textvariable=SleepTimer.get_instance().minutes, width=2, anchor='e').grid(row=0, column=1)
        ttk.Label(timerAdjustmentContainer, text="min").grid(row=0, column=2)
        ttk.Button(timerAdjustmentContainer, text=">", pad=(20, 5), style="Settings.TButton",
                   command=SleepTimer.get_instance().increment_minutes).grid(row=0, column=3, sticky="w", padx=10)


    def on_display_button_clicked(self):
        DisplaySetting.get_instance().change_state()
        self.updateDisplayButtonState()

    def on_cursor_button_clicked(self):
        CursorSetting.get_instance().change_state()

    def on_sleep_timer_button_clicked(self):
        SleepTimer.get_instance().change_state()
        self.updateSleepButtonState()

    def updateDisplayButtonState(self):
        if DisplaySetting.get_instance().displayState.get() == 'On':
            self.displayButton.state(['!alternate'])
        else:
            self.displayButton.state(['alternate'])

    def updateSleepButtonState(self):
        if SleepTimer.get_instance().enabled.get():
            self.sleepButton.state(['!alternate'])
        else:
            self.sleepButton.state(['alternate'])

    def on_display_type_button_clicked(self):
        MainScreenTypeSetting.get_instance().change_main_screen()


class SettingsTab(ttk.Frame):

    def __init__(self, menu_delegate, container):
        super().__init__(container)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.menuDelegate = menu_delegate

        self.container = ttk.Frame(self, pad=30)
        self.container.grid_propagate(False)
        self.container.grid(row=0, column=0, sticky="wnes")
        self.container.rowconfigure(1, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.createPersonalizationText()
        self.lazy_tuner_notebook = None
        self.createAdditionalSettingsContainer()
        self.createCloseButton()

    def limitPersonalizationTextLength(self):
        text = Config.get_instance().customDeviceNameVar.get()
        if len(text) > 20:
            Config.get_instance().customDeviceNameVar.set(text[:20])

    def createPersonalizationText(self):
        container = ttk.Frame(self.container)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.grid(row=0, column=0, sticky="wnes", pady=(0,10))
        ttk.Label(container, text="Personalization Text").grid(row=0, column=0)
        entry = ttk.Entry(container, textvariable=Config.get_instance().customDeviceNameVar, font=("Lato", 18), style="Config.TEntry")
        entry.bind("<ButtonRelease-1>", lambda e: Keyboard(self, Config.get_instance().customDeviceNameVar, lambda: Config.get_instance().saveCustomDeviceName()))
        entry.bind("")
        entry.grid(row=0, column=1, padx=(10, 0), sticky="we")
        Config.get_instance().customDeviceNameVar.trace("w", lambda *args: self.limitPersonalizationTextLength())

    def createAdditionalSettingsContainer(self):
        container = ttk.Frame(self.container, pad=(0, 10, 0, 10))
        container.grid_propagate(False)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=2, uniform="fred")
        container.columnconfigure(2, weight=3, uniform="fred")
        container.grid(row=1, column=0, columnspan=2, sticky="wnes")


        GeneralSettings(container).grid(row=0, column=0, sticky="wnes")

        self.lazy_tuner_notebook = LazyNotebook(container)
        self.lazy_tuner_notebook.grid(row=0, column=2, sticky="wnes")
        self.lazy_tuner_notebook.add(lambda master: TunerOnOffSettings(master, pad=15), "Tuner On / Off", lambda tab: tab.refresh_tuner_on_off_booleans())
        self.lazy_tuner_notebook.add(lambda master: TunerStorageSettings(master, InterfaceWrapper.getInstance().get_storage_bank(), pad=15), "Tuner Settings Storage", lambda tab: tab.update_ext_antenna_state())





    def createCloseButton(self):
        ttk.Button(self.container, text="Close", pad=(40, 20), style="Settings.TButton", command=self.onCloseClicked) \
            .grid(row=3, column=1, sticky="se")

    def onCloseClicked(self):
        self.menuDelegate.onCloseClicked()
