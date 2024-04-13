import sys
import os
from customlogging import log

from bootConfig import update_boot_config_if_outdated
from config import CURRENT_GUI_FOLDER



def restart_with_additional_ld_path(new_lib):
    restart = False
    if os.environ.get('LD_LIBRARY_PATH') is None:
        os.environ['LD_LIBRARY_PATH'] = new_lib
        restart = True
    else:
        if new_lib not in os.environ.get('LD_LIBRARY_PATH'):
            os.environ['LD_LIBRARY_PATH'] += ':' + new_lib
            restart = True
    if restart:
        try:
            os.execv(sys.executable, ['python3'] + sys.argv)
        except Exception as e:
            sys.exit('EXCEPTION: Failed to Execute under modified environment, ' + str(e))


restart_with_additional_ld_path('{}/hamlib/lib'.format(CURRENT_GUI_FOLDER))

log("============ APPLICATION STARTUP =============")

from displaySetting import DisplaySetting
from main_screen.operating_buttons import OperatingButtons
from main_screen.scale import NeedleScale, BarScale, Scale
from main_screen.status import StatusBar
from main_screen.tuners import NoTuner, Tuner, ManualTuner
from sleepTimer import SleepTimer
from scaleTypeSetting import ScaleTypeSetting
from tkinter import ttk, Tk, FALSE

from restartScreen import RestartScreen, RestartMessage
from themes import initThemes, useDarkTheme, useMenuTheme
from data import Data, ControllerVersionException
from config import Config
from cursorSetting import CursorSetting
from operationalInterface import OperationalInterfaceControl
from dimensions import DIMENSIONS
from menu.menu import Menu
from localUpdateScreen import LocalUpdateScreen
from updateInProgress import UpdateInProgress

from rest_server.restServer import RestServerSupport
from canBus.canConnectorFactory import CanConnectorFactory

from interface import InterfaceWrapper


class Antennas(ttk.Frame):

    def __init__(self, container):
        super().__init__(container, padding=(20, 5))
        self.grid(row=2, column=0, sticky="wnes")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.antenna_container = None
        self.external_antenna_container = None
        self.antennaButtons = list()
        self.createAntenna()
        self.update_antenna_buttons()

    def createAntenna(self):
        self.antenna_container = ttk.Frame(self)
        self.antenna_container.grid(row=0, column=0, sticky="nwes")
        self.antenna_container.rowconfigure(0, weight=1)
        self.antenna_container.columnconfigure(0, weight=1)

        for i in range(0, 4):
            self.antenna_container.columnconfigure(i, weight=1, uniform='fred')
            antenna_button = ttk.Radiobutton(self.antenna_container, variable=Data.getInstance().vars.curAntenna, value=i,
                                            textvariable=Config.get_instance().customAntennaNameVars[i], pad=(5, 5), style="Antenna.Toolbutton",
                                            command=self.on_antenna_clicked)
            antenna_button.grid(row=0, column=i, padx=5, sticky="nwes")
            self.antennaButtons.append(antenna_button)

        self.external_antenna_container = ttk.Frame(self)
        self.external_antenna_container.columnconfigure(1, weight=1)
        self.external_antenna_container.rowconfigure(0, weight=1)
        self.external_antenna_container.grid(row=0, column=0, sticky="nwes")
        ext_antenna_buttonlike_frame = ttk.Frame(self.external_antenna_container, padding=(20, 5), style="Selected.Antenna.Toolbutton.TFrame")
        ext_antenna_buttonlike_frame.grid(row=0, column=0, padx=5)
        ttk.Label(ext_antenna_buttonlike_frame, text='External Antenna',
                  style="Antenna.Toolbutton.TLabel").grid(row=0, column=0)
        ttk.Label(ext_antenna_buttonlike_frame, textvariable=Data.getInstance().vars.curExtAntennaNumberString,
                  style="Selected.Antenna.Toolbutton.TLabel").grid(row=0, column=1, padx=(20,0))

    def is_antenna_change_allowed(self):
        return not (Data.getInstance().PTT or Data.getInstance().tunerState == Data.TunerState.AUTO_TUNING or Data.getInstance().tunerState == Data.TunerState.AUTO_TUNING_FROM_AUTO)

    def simulate_on_antenna_clicked(self, antenna_index):
        Data.getInstance().vars.curAntenna.set(antenna_index)
        return self.on_antenna_clicked()

    def on_antenna_clicked(self):
        if not self.is_antenna_change_allowed():
            return False
        new_antenna = Data.getInstance().vars.curAntenna.get()
        InterfaceWrapper.getInstance().set_antenna(new_antenna)
        Data.getInstance().defaultAntennas[Data.getInstance().curBand] = new_antenna
        return True

    def update_antenna_buttons(self):
        if Data.getInstance().useExternalAntenna:
            self.antenna_container.lower(self.external_antenna_container)
        else:
            self.antenna_container.lift(self.external_antenna_container)
            selected_antennas = Config.get_instance().selectedAntennasPerBand[Data.getInstance().curBand]
            for i, antenna_is_selected in enumerate(selected_antennas):
                if antenna_is_selected.get():
                    self.antennaButtons[i].configure(state='!disabled')
                else:
                    self.antennaButtons[i].configure(state='disabled')


class HardwareStatistics(ttk.Frame):

    def __init__(self, delegate, container):
        super().__init__(container, padding=(20, 5))
        self.grid(row=3, column=0, sticky="wnes")

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=6, uniform="fred")
        self.columnconfigure(1, weight=3, uniform="fred")
        self.columnconfigure(2, weight=2, uniform="fred")
        self.columnconfigure(3, weight=2, uniform="fred")

        self.delegate = delegate

        self.createCurrentBand()
        self.createHardware()
        self.createMenu()

    def createCurrentBand(self):
        band_frame = ttk.Frame(self)
        band_frame.rowconfigure(0, weight=1)
        band_frame.columnconfigure(1, weight=1)
        band_frame.grid(row=0, column=0, rowspan=2, sticky="wnes")
        ttk.Label(band_frame, text="Band: ", style="Band.TLabel", anchor="w").grid(row=0, column=0, sticky="wnes")
        ttk.Label(band_frame, textvariable=Data.getInstance().vars.curBand, style="Yellow.Band.TLabel", anchor="w")\
            .grid(row=0, column=1, sticky="wnes")

    def createHardware(self):
        ttk.Label(self, textvariable=Data.getInstance().vars.temperature, anchor="e", style="Hardware.TLabel")\
            .grid(row=0, column=1, rowspan=2, sticky="wnes")
        ttk.Label(self, textvariable=Data.getInstance().vars.voltage, anchor="e", style="Green.Hardware.TLabel")\
            .grid(row=0, column=2, sticky="wes")
        ttk.Label(self, textvariable=Data.getInstance().vars.current, anchor="e", style="Hardware.TLabel")\
            .grid(row=1, column=2, sticky="wne")

    def createMenu(self):
        menu = ttk.Label(self, text="Menu", anchor="center", pad=(10, 15), style="Menu.TLabel")
        menu.bind("<ButtonRelease-1>", self.onMenuClicked)
        menu.grid(row=0, column=3, rowspan=2)

    def onMenuClicked(self, _):
        self.delegate.onMenuClicked()


class DeviceName(ttk.Frame):

    def __init__(self, container):
        super().__init__(container, padding=(20, 5))
        self.grid(row=4, column=0, sticky="wnes")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.createDeviceName()

    def createDeviceName(self):
        ttk.Label(self, textvariable=Data.getInstance().vars.deviceName, anchor="sw", style="Device.TLabel")\
            .grid(row=0, column=0, sticky="wnes")


class ScaleStatistics(ttk.Frame):

    def __init__(self, container):
        super().__init__(container)
        self.grid(row=0, column=0, sticky="we")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.createFrequency()

    def createFrequency(self):
        ttk.Label(self, textvariable=Data.getInstance().vars.f_m, anchor="center", style="Frequency.TLabel")\
            .grid(row=0, column=0, pady=7, sticky="we")


class VersionAndCopyright(ttk.Frame):

    def __init__(self, container):
        super().__init__(container)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.grid(row=3, column=0, sticky="we")

        self.createLabel()

    def createLabel(self):
        ttk.Label(self, textvariable=Data.getInstance().vars.version, pad=(10, 10), anchor="e", style="VersionAndCopyright.TLabel")\
            .grid(row=0, column=0, sticky="wnes")


class App(Tk):

    def init_controller(self):
        if Config.get_instance().isLowPower.get():
            InterfaceWrapper.getInstance().setHighLowPower(0)
        else:
            InterfaceWrapper.getInstance().setHighLowPower(1)

    def __init__(self):
        super().__init__()
        # Initialize the themes, we need to call this after super.__init__ of the app
        initThemes(self)

        # before calling any other interface methods, first check controller version:
        try:
            Data.getInstance()
        except ControllerVersionException as e:
            useMenuTheme()
            localUpdateScreen = LocalUpdateScreen(e.actualVersion, e.minVersion, self, self)
            localUpdateScreen.focus()
            return

        must_be_restarted = update_boot_config_if_outdated()
        if must_be_restarted:
            useMenuTheme()
            restart_screen = RestartScreen(RestartMessage.SYSTEM_CONFIG_APPLIED, self)
            restart_screen.focus()
            return

        self.init_controller()

        CanConnectorFactory.get_can_connector_instance().initialize_power_supply()
        CanConnectorFactory.get_can_connector_instance().start_receiving()

        self.title("RF-KIT")
        useDarkTheme()

        # get cursor managed
        CursorSetting.get_instance().manage_cursor_for(self)
        SleepTimer.get_instance().observe(self)

        # Make the window fullscreen and not resizable
        self.attributes("-fullscreen", True)
        self.resizable(FALSE, FALSE)
        self.geometry(f"{DIMENSIONS.APP_WIDTH}x{DIMENSIONS.APP_HEIGHT}")
        self.configure(background="#000000")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.container = ttk.Frame(self)
        self.container.grid(row=0, column=0, pady=(0, 20), sticky="wnes")

        self.fetchAndPushCatFrequencyJob = None
        self.operationalInterfaceRestoreJob = None

        self.debugMode = False

        # We currently only test for the debug start parameter
        for arg in sys.argv:
            if arg == "-d" or arg == "-D":
                self.debugMode = True
                break

        self.tunermode = False

        self.autoTuners = list()
        self.manualTuners = list()
        self.autoTuningTuners = list()
        self.autoTuningFromAutoTuners = list()
        self.noTuner = None

        OperationalInterfaceControl.initOperationalInterface()
        self.fetch_and_push_operational_interface_frequency()
        self.restore_operational_interface_when_fallback()

        self.needleScale = None
        self.barScale = None
        self.statusBar = None
        self.antennas = None
        self.hardwareStats = None
        self.deviceNames = None
        self.activeScale = None
        self.initWidgets()

        # Draw the scale
        self.needleScale.drawScaleAndNeedles()
        self.barScale.drawScaleAndBars()
        ScaleTypeSetting.get_instance().initialize_scale_setter(self.switchToScale, self.barScale, self.needleScale)
        self.tuner = None
        # Wait for fetchData to return to display the first tuner

        Data.getInstance().register_fetch_watcher(self.update_after_fetch)
        Data.getInstance().set_fetch_end(self.update_idletasks)
        Data.getInstance().start_fetching(self)
        log("Version: " + Data.getInstance().vars.version.get())

        DisplaySetting.get_instance().apply_on_startup(self)

        self.restServerSupport = RestServerSupport(
            lambda op: self.operatingButtons.standbyOperate.onStandbyOperateClicked(None, op),
            lambda: self.operatingButtons.reset.onResetClicked(),
            lambda: self.antennas.is_antenna_change_allowed(),
            lambda antenna_index: self.antennas.simulate_on_antenna_clicked(antenna_index)
        )
        self.restServerSupport.start_rest_server()

        self.update_idletasks()

    def fetch_and_push_operational_interface_frequency(self):
        if not Data.getInstance().PTT:
            OperationalInterfaceControl.operationalInterface.get_and_push_frequency()
        self.fetchAndPushCatFrequencyJob = self.after(20, self.fetch_and_push_operational_interface_frequency)

    def restore_operational_interface_when_fallback(self):
        if OperationalInterfaceControl.operationalInterface.is_fallback():
            OperationalInterfaceControl.operationalInterface.try_restore()
        self.operationalInterfaceRestoreJob = self.after(100, self.restore_operational_interface_when_fallback)

    def initWidgets(self):
        self.initLeftContainer()
        self.initRightContainer()
        self.initInterface()
        self.initCustomDeviceName()

    def initCustomDeviceName(self):
        ttk.Label(self.container, textvariable=Config.get_instance().customDeviceNameVar, anchor="s", style="Custom.Device.TLabel").grid(row=0, column=0, columnspan=3, sticky="s")

    def initLeftContainer(self):
        leftContainer = ttk.Frame(self.container, width=DIMENSIONS.SCALE_WIDTH, height=(DIMENSIONS.APP_HEIGHT - DIMENSIONS.SCREEN_BOTTOM_UNUSABLE_SPACE))
        leftContainer.grid_propagate(False)
        leftContainer.rowconfigure(1, weight=3, uniform="fred")
        leftContainer.rowconfigure(2, weight=4, uniform="fred")
        leftContainer.rowconfigure(3, weight=6, uniform="fred")
        leftContainer.rowconfigure(4, weight=3, uniform="fred")
        leftContainer.columnconfigure(0, weight=1)
        leftContainer.grid(row=0, column=0)

        # Create all widgets for the left container
        self.needleScale = NeedleScale(leftContainer, ScaleTypeSetting.get_instance().change_display_type)
        self.needleScale.grid(row=0, column=0, sticky="we")
        self.barScale = BarScale(leftContainer, ScaleTypeSetting.get_instance().change_display_type)
        self.barScale.grid(row=0, column=0, sticky="we")
        self.statusBar = StatusBar(leftContainer)
        self.statusBar.grid(row=1, column=0, sticky="wnes")
        self.antennas = Antennas(leftContainer)
        self.hardwareStats = HardwareStatistics(self, leftContainer)
        self.deviceNames = DeviceName(leftContainer)

    def initRightContainer(self):
        rightContainer = ttk.Frame(self.container, width=DIMENSIONS.TUNER_WIDTH, height=(DIMENSIONS.APP_HEIGHT - DIMENSIONS.SCREEN_BOTTOM_UNUSABLE_SPACE))
        rightContainer.grid_propagate(False)
        rightContainer.rowconfigure(2, weight=1)
        rightContainer.columnconfigure(0, weight=1)
        rightContainer.grid(row=0, column=1)

        self.scaleStats = ScaleStatistics(rightContainer)
        self.initTuners(rightContainer)
        self.operatingButtons = OperatingButtons(rightContainer)
        self.operatingButtons.grid(row=2, column=0, sticky="we")
        self.versionAndCopyright = VersionAndCopyright(rightContainer)

    def initInterface(self):
        container = ttk.Frame(self.container, width=DIMENSIONS.INTERFACE_WIDTH)
        container.grid_propagate(False)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1, uniform="fred")
        container.rowconfigure(1, weight=1, uniform="fred")
        container.rowconfigure(2, weight=1, uniform="fred")
        container.grid(row=0, column=2, sticky="wnes")
        interfaceButton = ttk.Label(container, textvariable=OperationalInterfaceControl.operationalInterface.currentOperationalInterfaceDisplayName, anchor="n", style="Interface.TLabel")
        interfaceButton.bind("<ButtonRelease-1>", self.onInterfaceClicked)
        interfaceButton.grid(row=0, column=0, sticky="wnes")
        self.ptt = ttk.Label(container, text="PTT", anchor="center", style="Active.Status.TLabel")
        self.ptt.grid(row=1, column=0, sticky="wnes")
        self.bias = ttk.Label(container, text="BIAS", anchor="s", style="Active.Status.TLabel")
        self.bias.grid(row=2, column=0, sticky="wnes")

    def initTuners(self, container):
        # Auto Tuners
        self.autoTuners.append(Tuner(self, container, Tuner.TunerType.AUTO, Tuner.TunerSubType.CL))
        self.autoTuners.append(Tuner(self, container, Tuner.TunerType.AUTO, Tuner.TunerSubType.LC))
        self.autoTuners.append(Tuner(self, container, Tuner.TunerType.AUTO, Tuner.TunerSubType.BYPASS))
        for tuner in self.autoTuners:
            tuner.grid(row=1, column=0, sticky="nswe")
        # Manual Tuners
        self.manualTuners.append(ManualTuner(self, container, Tuner.TunerSubType.CL))
        self.manualTuners.append(ManualTuner(self, container, Tuner.TunerSubType.LC))
        self.manualTuners.append(ManualTuner(self, container, Tuner.TunerSubType.BYPASS))
        for tuner in self.manualTuners:
            tuner.grid(row=1, column=0, sticky="nswe")
        # Auto Tuning Tuners
        self.autoTuningTuners.append(Tuner(self, container, Tuner.TunerType.AUTO_TUNING, Tuner.TunerSubType.CL))
        self.autoTuningTuners.append(Tuner(self, container, Tuner.TunerType.AUTO_TUNING, Tuner.TunerSubType.LC))
        self.autoTuningTuners.append(Tuner(self, container, Tuner.TunerType.AUTO_TUNING, Tuner.TunerSubType.BYPASS))
        for tuner in self.autoTuningTuners:
            tuner.grid(row=1, column=0, sticky="nswe")
        # Auto Tuning Tuners
        self.autoTuningFromAutoTuners.append(Tuner(self, container, Tuner.TunerType.AUTOTUNE_FROM_AUTO, Tuner.TunerSubType.CL))
        self.autoTuningFromAutoTuners.append(Tuner(self, container, Tuner.TunerType.AUTOTUNE_FROM_AUTO, Tuner.TunerSubType.LC))
        self.autoTuningFromAutoTuners.append(Tuner(self, container, Tuner.TunerType.AUTOTUNE_FROM_AUTO, Tuner.TunerSubType.BYPASS))
        for tuner in self.autoTuningFromAutoTuners:
            tuner.grid(row=1, column=0, sticky="nswe")
        # No Tuner
        self.noTuner = NoTuner(container)
        self.noTuner.grid(row=1, column=0, sticky="nswe")

    def getTunerFor(self, state, tunerSubType, bypass):
        if state == Data.TunerState.OFF:
            return self.noTuner
        elif state == Data.TunerState.MANUAL:
            tuners = self.manualTuners
        elif state == Data.TunerState.AUTO_TUNING:
            tuners = self.autoTuningTuners
        elif state == Data.TunerState.AUTO_TUNING_FROM_AUTO:
            tuners = self.autoTuningFromAutoTuners
        else:
            tuners = self.autoTuners
        for tuner in tuners:
            if bypass or state == Data.TunerState.BYPASS:
                if tuner.tunerSubType == Tuner.TunerSubType.BYPASS:
                    return tuner
            elif tunerSubType == tuner.tunerSubType:
                return tuner
        return None

    def switchToScale(self, scale: Scale):
        scale.lift()
        self.activeScale = scale

    def onInterfaceClicked(self, event):
        OperationalInterfaceControl.operationalInterface.switch_operational_interface()

    def onKClicked(self, tuner):
        if Data.getInstance().tunerState != Data.TunerState.MANUAL:
            return
        if tuner.tunerType != Tuner.TunerType.MANUAL or\
           (tuner.tunerSubType != Tuner.TunerSubType.CL and
            tuner.tunerSubType != Tuner.TunerSubType.LC):

            return

        InterfaceWrapper.getInstance().set_K(
            Tuner.TunerSubType.CL.value if tuner.tunerSubType != Tuner.TunerSubType.CL else Tuner.TunerSubType.LC.value)
        # We determine the newly shown tuner based on the tuner state, K and bypass returned by the interface

    def onTunerModeClicked(self, tuner):
        if Data.getInstance().tunerState == Data.TunerState.AUTO_TUNING:
            return
        InterfaceWrapper.getInstance().set_tuner_auto(tuner.tunerType == Tuner.TunerType.MANUAL)
        # We determine the newly shown tuner based on the tuner state, K and bypass returned by the interface

    def onBypassClicked(self, tuner):
        if Data.getInstance().tunerState == Data.TunerState.AUTO_TUNING:
            return
        InterfaceWrapper.getInstance().set_tuner_bypass(0 if tuner.tunerSubType == Tuner.TunerSubType.BYPASS else 1)
        # We determine the newly shown tuner based on the tuner state, K and bypass returned by the interface

    # currently not called when running as the handler which is calling this method is not bound to any button
    def onTuneClicked(self):
        self.tunermode = not self.tunermode
        InterfaceWrapper.getInstance().set_tunermode(self.tunermode)
        for tuner in self.manualTuners:
            tuner.updateForTunermode(self.tunermode)

    def onMenuClicked(self):
        self.restServerSupport.stop_rest_server()
        Data.getInstance().stop_fetching()  #TODO also cancel cat frequency?
        menu = Menu(self, self)
        useMenuTheme()
        menu.focus()

    def onMenuClose(self):
        useDarkTheme()
        Data.getInstance().start_fetching(self)
        self.restServerSupport.start_rest_server()

    def onUpdateClicked(self, updateDelegate, filepath=None, startup=False):
        self.updateDelegate = updateDelegate
        if not startup:
            Data.getInstance().stop_fetching()
            self.cancelFetchAndPushCatFrequency() # TODO ensure univ mode?
            CanConnectorFactory.get_can_connector_instance().stop_receiving()
        updateInProgress = UpdateInProgress(self, self, filepath)
        useMenuTheme()
        updateInProgress.focus()

    def onUpdateFailed(self):
        self.updateDelegate.onUpdateFailed()

    def onUpdateFinished(self):
        self.updateDelegate.onUpdateFinished()
        # Normally the handling of `this` would be before the updateDelegate handling

        # Show the restart screen
        restartScreen = RestartScreen(RestartMessage.UPDATED, self)
        restartScreen.focus()

    def updateTunerForFetchData(self):
        newTuner = self.getTunerFor(Data.getInstance().tunerState, Tuner.TunerSubType(Data.getInstance().K), Data.getInstance().bypass)
        if newTuner != self.tuner:
            self.tuner = newTuner
            newTuner.show()
        newTuner.update_after_fetch_data()

    def update_after_fetch(self):
        self.activeScale.update_scale()
        self.updateTunerForFetchData()
        self.antennas.update_antenna_buttons()  # fetchData is called also on menu close
        self.ptt.configure(style="Active.Status.TLabel") if Data.getInstance().PTT else self.ptt.configure(style="Inactive.Status.TLabel")
        self.bias.configure(style="Active.Status.TLabel") if Data.getInstance().BIAS else self.bias.configure(style="Inactive.Status.TLabel")

    def cancelFetchAndPushCatFrequency(self):
        if self.fetchAndPushCatFrequencyJob is None:
            return
        self.after_cancel(self.fetchAndPushCatFrequencyJob)
        self.fetchAndPushCatFrequencyJob = None

    def onCloseApplication(self):
        self.destroy()
        # window has to be removed from cursor management to prevent errors on next cursor change
        CursorSetting.get_instance().stop_managing_cursor_for(self)
        SleepTimer.get_instance().stop_observing(self)


if __name__ == "__main__":
    app = App()
    app.mainloop()
    InterfaceWrapper.getInstance().close()

