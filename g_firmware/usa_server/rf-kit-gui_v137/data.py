from enum import Enum
from tkinter import *

from customlogging import log
from interface import InterfaceWrapper, InterfaceException
from config import Config
from display import Display
from enums import Generation
from sleepTimer import SleepTimer

BAND_VALUES = [6, 10, 12, 15, 17, 20, 30, 40, 60, 80, 160]
BANDS = [str(value) + "m" for value in BAND_VALUES]

class ControllerVersionException(Exception):
    def __init__(self, min_version, actual_version):
        self.minVersion = min_version
        self.actualVersion = actual_version


class Data:

    instance = None

    class TunerState(Enum):

        BYPASS = 0
        MANUAL = 1
        AUTO_TUNING = 2
        AUTO = 3
        OFF = 4

    class ErrorState(Enum):

        NONE = 0
        HIGH_ANTENNA_REFLECTION = 1
        HIGH_CURRENT = 2
        HIGH_INPUT_POWER = 3
        SEVERE_ERROR_LPF = 4
        WRONG_FREQUENCY = 5
        NO_INTERNAL_HIGH_VOLTAGE = 6
        OVERHEATING = 7
        NOT_TUNED = 8
        HIGH_OUTPUT_POWER = 9
        HIGH_SWR = 10

        def __str__(self):
            if self == self.HIGH_ANTENNA_REFLECTION:
                return "High Antenna Reflection"
            if self == self.HIGH_CURRENT:
                return "High Current"
            if self == self.HIGH_INPUT_POWER:
                return "High Input Power"
            if self == self.SEVERE_ERROR_LPF:
                return "Severe Error LPF"
            if self == self.WRONG_FREQUENCY:
                return "Wrong Frequency"
            if self == self.NO_INTERNAL_HIGH_VOLTAGE:
                return "No internal high voltage"
            if self == self.OVERHEATING:
                return "Overheating"
            if self == self.HIGH_OUTPUT_POWER:
                return "High Output Power"
            if self == self.HIGH_SWR:
                return "High SWR"
            return ""

    class Vars:

        def __init__(self, generation):
            # Device
            self.deviceName = StringVar(value=str(generation))

            self.version = StringVar()

            self.status = StringVar()

            self.P_F = StringVar()
            self.P_dF = StringVar()
            self.P_dAF = StringVar()
            self.P_dR = StringVar()

            # Tuner
            self.f_m = StringVar()
            self.segmentSize = StringVar()
            self.f_t = StringVar()
            self.L = StringVar()
            self.C = StringVar()

            # Operational Parameters
            self.curAntenna = IntVar()
            self.curBand = StringVar()
            self.voltage = StringVar()
            self.current = StringVar()
            self.temperature = StringVar()
            self.useExtAntenna = IntVar()
            self.curExtAntennaNumberString = StringVar()

            # Scale
            self.forwardValueVar = StringVar()
            self.reflectedValueVar = StringVar()
            self.swrValueVar = StringVar()

    @classmethod
    def getInstance(cls):
        if cls.instance is None:
            cls.instance = Data()
        return cls.instance

    def __init__(self):
        self.guiVersion = 137
        self.minimumControllerVersion = 155

        self.ftpConfig = None

        self.defaultAntennas = None

        self.version = self.init_and_check_controller_version()
        self.calibrated = False
        self.voltage = 0.
        self.current = 0.
        self.temperature = 0.
        self.P_dF = 0.
        self.P_F = 0.
        self.max_P_F = 0.
        self.overall_max_P_F = 0.
        self.P_dAF = 0.
        self.P_AF = 0.
        self.P_dR = 0.
        self.P_R = 0.
        self.max_P_R = 0.
        self.overall_max_P_R = 0.
        self.SWR = 0
        self.max_SWR = 0
        self.overall_max_SWR = 0.
        self.f_m = 0
        self.filter = 0
        self.f_t = 0
        self.L = 0
        self.C = 0
        self.bypass = False
        self.K = 0
        self.PTT = False
        self.BIAS = False
        self.segmentSize = 0
        self.curBand = 0
        self.curAntenna = 0
        self.tunerState = self.TunerState.MANUAL
        self.inOperate = False
        self.errorState = self.ErrorState.NONE
        self.biasPercentage = 0.
        self.adjustment = 0

        self.useExternalAntenna = False

        self.generation = Generation(InterfaceWrapper.getInstance().get_generation())
        Display.get_instance().init_for_generation(self.generation)

        # Tkinter Variables
        self.vars = self.Vars(self.generation)

        # updateAll does not retrieve the default antennas nor the extAntennaHighLowActive, so we do it once here
        self.defaultAntennas = InterfaceWrapper.getInstance().get_default_antennas()
        self.externalAntennaHighLowActive = InterfaceWrapper.getInstance().get_ext_antenna_high_low_active()

        self.updateAll()
        Config.get_instance().ensure_consistency_with(self.defaultAntennas)

        self.fetchDataJob = None
        self.fetchJobMaster = None
        self.fetchWatchers = set()

    def init_and_check_controller_version(self):
        actual_controller_version = InterfaceWrapper.getInstance().get_all_values()[0]
        if self.minimumControllerVersion > actual_controller_version:
            raise ControllerVersionException(self.minimumControllerVersion, actual_controller_version)
        return actual_controller_version

    def start_fetching(self, job_master):
        if self.fetchDataJob is not None:
            if self.fetchJobMaster == job_master:
                return
            else:
                self.stop_fetching()
        self.fetchJobMaster = job_master
        self.fetch_data_job()

    def stop_fetching(self):
        if self.fetchDataJob is None:
            return
        self.fetchJobMaster.after_cancel(self.fetchDataJob)
        self.fetchDataJob = None
        self.fetchJobMaster = None

    def register_fetch_watcher(self, watcher_callable):
        self.fetchWatchers.add(watcher_callable)

    def unregister_fetch_watcher(self, watcher_callable):
        self.fetchWatchers.remove(watcher_callable)

    def fetch_data_job(self):
        try:  # TODO extra class for interface-calling jobs
            self.fetch_data_once()
        except InterfaceException as e:
            log("WARNING: interface error while getting values: " + str(e))
        self.fetchDataJob = self.fetchJobMaster.after(40, self.fetch_data_job)

    def fetch_data_once(self):
        self.updateAll()
        for watcher in self.fetchWatchers:
            watcher()

    def updateBIASPercentage(self):
        self.biasPercentage = InterfaceWrapper.getInstance().get_offset_BIAS()

    def updateAll(self):
        self.updateAllValues()
        self.updateAllVars()

    def updateAllValues(self):
        result = InterfaceWrapper.getInstance().get_all_values()
        self.version = result[0]
        self.calibrated = result[1]
        self.voltage = result[2]
        self.current = result[3]
        self.temperature = result[4]
        self.P_dF = result[5]
        self.P_F = result[6]
        self.P_dAF = result[7]
        self.P_AF = result[8]
        self.P_dR = result[9]
        self.P_R = result[10]
        self.SWR = result[11]
        self.f_m = result[12]
        self.filter = result[13]
        self.f_t = result[14]
        self.L = result[15]
        self.C = result[16]
        self.bypass = result[17]
        self.K = result[18]
        prevPTT = self.PTT
        self.PTT = result[19]
        self.BIAS = result[20]
        self.curBand = result[21]
        self.curAntenna = result[22]
        self.tunerState = self.TunerState(result[23])
        self.errorState = self.ErrorState(result[24])
        self.inOperate = result[25]
        self.adjustment = result[26]
        self.useExternalAntenna = result[27]
        if self.PTT:
            SleepTimer.get_instance().reset()
        else:
            self.P_dF = 0.
            self.P_F = 0.
            self.P_dAF = 0.
            self.P_AF = 0.
            self.P_dR = 0.
            self.P_R = 0.
            self.SWR = 1

        self.updateSegmentSize()

        self.updateMaxValues()
        self.updateOverallMaxValues(True if not prevPTT and self.PTT else False)

    # init
    forward_series = [0, 0]
    reflected_series = [0, 0]
    swr_series = [0, 0]

    # parameter
    series_max_len = 5

    def calculate_maximum(self, data_series, new_value):
        if len(data_series) >= self.series_max_len:
            data_series.pop(0)
        data_series.append(new_value)
        return max(data_series)

    def updateMaxValues(self):
        self.max_P_F = self.calculate_maximum(self.forward_series, self.P_F)
        self.max_P_R = self.calculate_maximum(self.reflected_series, self.P_R)
        self.max_SWR = self.calculate_maximum(self.swr_series, self.SWR)

    def updateOverallMaxValues(self, reset):
        self.overall_max_P_F = self.P_F if reset else max(self.overall_max_P_F, self.P_F)
        self.overall_max_P_R = self.P_R if reset else max(self.overall_max_P_R, self.P_R)
        self.overall_max_SWR = self.SWR if reset else max(self.overall_max_SWR, self.SWR)


    frequencyUnits = ["Hz", "kHz", "MHz", "GHz", "THz"]

    def getFrequencyString(self, frequency):
        return "{:d} kHz".format(int(frequency // 1000))
        unitIndex = 0
        while frequency > 1000 and unitIndex < (len(self.frequencyUnits) - 1):
            frequency /= 1000
            unitIndex += 1
        return "{:d} {:s}".format(int(frequency), self.frequencyUnits[unitIndex])

    def updateAllVars(self):
        self.vars.version.set("(RF-KIT PA Version G{:d}C{:d} © 2019-2023 by RF-KIT)".format(self.guiVersion, self.version))

        self.vars.status.set(self.errorState)

        self.vars.curBand.set(BANDS[self.curBand])
        self.vars.curAntenna.set(self.curAntenna)

        self.vars.P_F.set("{:.0f} W".format(self.P_F))
        self.vars.P_dF.set(str(self.P_dF))
        self.vars.P_dAF.set(str(self.P_dAF))
        self.vars.P_dR.set(str(self.P_dR))

        self.vars.voltage.set("{:.1f} V".format(self.voltage))
        self.vars.temperature.set("{:.1f} °C".format(self.temperature))
        self.vars.current.set("{:.1f} A".format(self.get_truncated_current()))

        self.vars.f_m.set(self.getFrequencyString(self.f_m))
        self.vars.segmentSize.set("Segment-Size: {:d} kHz".format(self.segmentSize))
        self.vars.f_t.set(self.getFrequencyString(self.f_t))
        self.vars.L.set("{:d} nH".format(self.L))
        self.vars.C.set("{:d} pF".format(self.C))

        self.vars.useExtAntenna.set(self.useExternalAntenna)
        if self.useExternalAntenna:
            self.vars.curExtAntennaNumberString.set(str(self.curAntenna + 1))  # only valid if useExtAntenna is true
        else:
            self.vars.curExtAntennaNumberString.set('')

        self.vars.forwardValueVar.set("({:.0f} W / {:.0f} W)".format(self.P_F, self.overall_max_P_F))
        self.vars.reflectedValueVar.set("({:.0f} W / {:.0f} W)".format(self.P_R, self.overall_max_P_R))
        self.vars.swrValueVar.set("({:.2f} / {:.2f})".format(self.SWR, self.overall_max_SWR))

    def get_truncated_current(self):
        return self.current if self.current >= 0.3 else 0.0

    filterSegmentSizes = [101, 75, 51, 25, 9, 9]

    def updateSegmentSize(self):
        self.segmentSize = self.filterSegmentSizes[self.filter]
