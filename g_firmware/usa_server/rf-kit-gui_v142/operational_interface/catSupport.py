import time
from enum import Enum
from customlogging import log


from config import Config, CURRENT_GUI_FOLDER

import sys
import multiprocessing
import ctypes


sys.path.append('{}/hamlib/lib/python3.7/site-packages'.format(CURRENT_GUI_FOLDER))
import Hamlib

class SupportedManufacturer(Enum):
    ADAT = ("ADAT by HB9CBU")
    ALINCO = ("Alinco")
 #   BARRETT = ("Barrett")
    ELAD = ("Elad")
    ELECRAFT = ("Elecraft")
    FLEXRADIO = ("Flexradio")
    ICOM = ("Icom")
    KENWOOD = ("Kenwood")
    TENTEC = ("TenTec")
    YAESU = ("Yaesu")

    def __init__(self, displayName):
        self.displayName = displayName
        self.supportedRigs = []

    @classmethod
    def by_display_name(cls):
        return dict([(man.displayName, man) for man in sorted(list(SupportedManufacturer), key=lambda m: m.displayName)])

class SupportedRig(Enum):
    YAESU_FT847 = (SupportedManufacturer.YAESU, "FT-847", Hamlib.RIG_MODEL_FT847)
    YAESU_FT1000 = (SupportedManufacturer.YAESU, "FT-1000", Hamlib.RIG_MODEL_FT1000)
    YAESU_FT1000D = (SupportedManufacturer.YAESU, "FT-1000D", Hamlib.RIG_MODEL_FT1000D)
    YAESU_FT1000MPMKV = (SupportedManufacturer.YAESU, "MARK-V FT-1000MP", Hamlib.RIG_MODEL_FT1000MPMKV)
    YAESU_FT747 = (SupportedManufacturer.YAESU, "FT-747", Hamlib.RIG_MODEL_FT747)
    YAESU_FT757 = (SupportedManufacturer.YAESU, "FT-757", Hamlib.RIG_MODEL_FT757)
    YAESU_FT757GXII = (SupportedManufacturer.YAESU, "FT-757GXII", Hamlib.RIG_MODEL_FT757GXII)
    YAESU_FT575 = (SupportedManufacturer.YAESU, "FT-575", Hamlib.RIG_MODEL_FT575)
    YAESU_FT767 = (SupportedManufacturer.YAESU, "FT-767", Hamlib.RIG_MODEL_FT767)
    YAESU_FT840 = (SupportedManufacturer.YAESU, "FT-840", Hamlib.RIG_MODEL_FT840)
    YAESU_FT820 = (SupportedManufacturer.YAESU, "FT-820", Hamlib.RIG_MODEL_FT820)
    YAESU_FT900 = (SupportedManufacturer.YAESU, "FT-900", Hamlib.RIG_MODEL_FT900)
    YAESU_FT920 = (SupportedManufacturer.YAESU, "FT-920", Hamlib.RIG_MODEL_FT920)
    YAESU_FT890 = (SupportedManufacturer.YAESU, "FT-890", Hamlib.RIG_MODEL_FT890)
    YAESU_FT990 = (SupportedManufacturer.YAESU, "FT-990", Hamlib.RIG_MODEL_FT990)
    YAESU_FT817 = (SupportedManufacturer.YAESU, "FT-817", Hamlib.RIG_MODEL_FT817)
    YAESU_FT100 = (SupportedManufacturer.YAESU, "FT-100", Hamlib.RIG_MODEL_FT100)
    YAESU_FT857 = (SupportedManufacturer.YAESU, "FT-857", Hamlib.RIG_MODEL_FT857)
    YAESU_FT897 = (SupportedManufacturer.YAESU, "FT-897", Hamlib.RIG_MODEL_FT897)
    YAESU_FT1000MP = (SupportedManufacturer.YAESU, "FT-1000MP", Hamlib.RIG_MODEL_FT1000MP)
    YAESU_FT1000MPMKVFLD = (SupportedManufacturer.YAESU, "MARK-V Field FT-1000MP", Hamlib.RIG_MODEL_FT1000MPMKVFLD)
    YAESU_FT450 = (SupportedManufacturer.YAESU, "FT-450", Hamlib.RIG_MODEL_FT450)
    YAESU_FT950 = (SupportedManufacturer.YAESU, "FT-950", Hamlib.RIG_MODEL_FT950)
    YAESU_FT2000 = (SupportedManufacturer.YAESU, "FT-2000", Hamlib.RIG_MODEL_FT2000)
    YAESU_FT9000 = (SupportedManufacturer.YAESU, "FT-9000", Hamlib.RIG_MODEL_FT9000)
    YAESU_FT980 = (SupportedManufacturer.YAESU, "FT-980", Hamlib.RIG_MODEL_FT980)
    YAESU_FTDX5000 = (SupportedManufacturer.YAESU, "FTDX5000", Hamlib.RIG_MODEL_FTDX5000)
    YAESU_VX1700 = (SupportedManufacturer.YAESU, "VX-1700", Hamlib.RIG_MODEL_VX1700)
    YAESU_FT1200 = (SupportedManufacturer.YAESU, "FT-1200", Hamlib.RIG_MODEL_FT1200)
    YAESU_FT991 = (SupportedManufacturer.YAESU, "FT-991", Hamlib.RIG_MODEL_FT991)
    YAESU_FT891 = (SupportedManufacturer.YAESU, "FT-891", Hamlib.RIG_MODEL_FT891)
    YAESU_FTDX3000 = (SupportedManufacturer.YAESU, "FTDX3000", Hamlib.RIG_MODEL_FTDX3000)
    YAESU_FT847UNI = (SupportedManufacturer.YAESU, "FT-847UNI", Hamlib.RIG_MODEL_FT847UNI)
    YAESU_FT600 = (SupportedManufacturer.YAESU, "FT-600", Hamlib.RIG_MODEL_FT600)
    YAESU_FTDX101D = (SupportedManufacturer.YAESU, "FT-DX101D", Hamlib.RIG_MODEL_FTDX101D)
    YAESU_FT818 = (SupportedManufacturer.YAESU, "FT-818", Hamlib.RIG_MODEL_FT818)
    KENWOOD_TS50 = (SupportedManufacturer.KENWOOD, "TS50", Hamlib.RIG_MODEL_TS50)
    KENWOOD_TS440 = (SupportedManufacturer.KENWOOD, "TS440", Hamlib.RIG_MODEL_TS440)
    KENWOOD_TS450S = (SupportedManufacturer.KENWOOD, "TS450S", Hamlib.RIG_MODEL_TS450S)
    KENWOOD_TS570D = (SupportedManufacturer.KENWOOD, "TS570D", Hamlib.RIG_MODEL_TS570D)
    KENWOOD_TS690S = (SupportedManufacturer.KENWOOD, "TS690S", Hamlib.RIG_MODEL_TS690S)
    KENWOOD_TS811 = (SupportedManufacturer.KENWOOD, "TS811", Hamlib.RIG_MODEL_TS811)
    KENWOOD_TS850 = (SupportedManufacturer.KENWOOD, "TS850", Hamlib.RIG_MODEL_TS850)
    KENWOOD_TS870S = (SupportedManufacturer.KENWOOD, "TS870S", Hamlib.RIG_MODEL_TS870S)
    KENWOOD_TS940 = (SupportedManufacturer.KENWOOD, "TS940", Hamlib.RIG_MODEL_TS940)
    KENWOOD_TS950S = (SupportedManufacturer.KENWOOD, "TS950S", Hamlib.RIG_MODEL_TS950S)
    KENWOOD_TS950SDX = (SupportedManufacturer.KENWOOD, "TS950SDX", Hamlib.RIG_MODEL_TS950SDX)
    KENWOOD_TS2000 = (SupportedManufacturer.KENWOOD, "TS2000", Hamlib.RIG_MODEL_TS2000)
    KENWOOD_TS570S = (SupportedManufacturer.KENWOOD, "TS570S", Hamlib.RIG_MODEL_TS570S)
    ELECRAFT_K2 = (SupportedManufacturer.ELECRAFT, "K2", Hamlib.RIG_MODEL_K2)
    KENWOOD_TS930 = (SupportedManufacturer.KENWOOD, "TS930", Hamlib.RIG_MODEL_TS930)
    KENWOOD_TS680S = (SupportedManufacturer.KENWOOD, "TS680S", Hamlib.RIG_MODEL_TS680S)
    KENWOOD_TS140S = (SupportedManufacturer.KENWOOD, "TS140S", Hamlib.RIG_MODEL_TS140S)
    KENWOOD_TS480 = (SupportedManufacturer.KENWOOD, "TS480", Hamlib.RIG_MODEL_TS480)
    ELECRAFT_K3 = (SupportedManufacturer.ELECRAFT, "K3", Hamlib.RIG_MODEL_K3)
    KENWOOD_TS590S = (SupportedManufacturer.KENWOOD, "TS590S", Hamlib.RIG_MODEL_TS590S)
    FLEXRADIO_F6K = (SupportedManufacturer.FLEXRADIO, "Flex6xxx", Hamlib.RIG_MODEL_ELAD_FDM_DUO)
    KENWOOD_TS590SG = (SupportedManufacturer.KENWOOD, "TS590SG", Hamlib.RIG_MODEL_TS590SG)
 #   ELECRAFT_XG3 = (SupportedManufacturer.ELECRAFT, "Elecraft XG-3 signal generator", Hamlib.RIG_MODEL_XG3)
    KENWOOD_TS990S = (SupportedManufacturer.KENWOOD, "TS990S", Hamlib.RIG_MODEL_TS990S)
    KENWOOD_HPSDR = (SupportedManufacturer.KENWOOD, "OpenHPSDR, PiHPSDR", Hamlib.RIG_MODEL_HPSDR)
    KENWOOD_TS890S = (SupportedManufacturer.KENWOOD, "TS890S", Hamlib.RIG_MODEL_TS890S)
    ELECRAFT_K3S = (SupportedManufacturer.ELECRAFT, "K3S", Hamlib.RIG_MODEL_K3S)
    ELECRAFT_KX2 = (SupportedManufacturer.ELECRAFT, "KX2", Hamlib.RIG_MODEL_KX2)
    ELECRAFT_KX3 = (SupportedManufacturer.ELECRAFT, "KX3", Hamlib.RIG_MODEL_KX3)
    KENWOOD_PT8000A = (SupportedManufacturer.KENWOOD, "PT8000A", Hamlib.RIG_MODEL_PT8000A)
    ELECRAFT_K4 = (SupportedManufacturer.ELECRAFT, "K4", Hamlib.RIG_MODEL_K3)
    KENWOOD_POWERSDR = (SupportedManufacturer.KENWOOD, "POWERSDR", Hamlib.RIG_MODEL_POWERSDR)
    ICOM_IC706 = (SupportedManufacturer.ICOM, "IC706", Hamlib.RIG_MODEL_IC706)
    ICOM_IC706MKII = (SupportedManufacturer.ICOM, "IC706MKII", Hamlib.RIG_MODEL_IC706MKII)
    ICOM_IC706MKIIG = (SupportedManufacturer.ICOM, "IC706MKIIG", Hamlib.RIG_MODEL_IC706MKIIG)
    ICOM_IC707 = (SupportedManufacturer.ICOM, "IC707", Hamlib.RIG_MODEL_IC707)
    ICOM_IC718 = (SupportedManufacturer.ICOM, "IC718", Hamlib.RIG_MODEL_IC718)
    ICOM_IC725 = (SupportedManufacturer.ICOM, "IC725", Hamlib.RIG_MODEL_IC725)
    ICOM_IC726 = (SupportedManufacturer.ICOM, "IC726", Hamlib.RIG_MODEL_IC726)
    ICOM_IC728 = (SupportedManufacturer.ICOM, "IC728", Hamlib.RIG_MODEL_IC728)
    ICOM_IC729 = (SupportedManufacturer.ICOM, "IC729", Hamlib.RIG_MODEL_IC729)
    ICOM_IC731 = (SupportedManufacturer.ICOM, "IC731", Hamlib.RIG_MODEL_IC731)
    ICOM_IC735 = (SupportedManufacturer.ICOM, "IC735", Hamlib.RIG_MODEL_IC735)
    ICOM_IC736 = (SupportedManufacturer.ICOM, "IC736", Hamlib.RIG_MODEL_IC736)
    ICOM_IC737 = (SupportedManufacturer.ICOM, "IC737", Hamlib.RIG_MODEL_IC737)
    ICOM_IC738 = (SupportedManufacturer.ICOM, "IC738", Hamlib.RIG_MODEL_IC738)
    ICOM_IC746 = (SupportedManufacturer.ICOM, "IC746", Hamlib.RIG_MODEL_IC746)
    ICOM_IC751 = (SupportedManufacturer.ICOM, "IC751", Hamlib.RIG_MODEL_IC751)
    ICOM_IC751A = (SupportedManufacturer.ICOM, "IC751A", Hamlib.RIG_MODEL_IC751A)
    ICOM_IC756 = (SupportedManufacturer.ICOM, "IC756", Hamlib.RIG_MODEL_IC756)
    ICOM_IC756PRO = (SupportedManufacturer.ICOM, "IC756PRO", Hamlib.RIG_MODEL_IC756PRO)
    ICOM_IC761 = (SupportedManufacturer.ICOM, "IC761", Hamlib.RIG_MODEL_IC761)
    ICOM_IC765 = (SupportedManufacturer.ICOM, "IC765", Hamlib.RIG_MODEL_IC765)
    ICOM_IC775 = (SupportedManufacturer.ICOM, "IC775", Hamlib.RIG_MODEL_IC775)
    ICOM_IC781 = (SupportedManufacturer.ICOM, "IC781", Hamlib.RIG_MODEL_IC781)
    ICOM_IC756PROII = (SupportedManufacturer.ICOM, "IC756PROII", Hamlib.RIG_MODEL_IC756PROII)
    ICOM_IC703 = (SupportedManufacturer.ICOM, "IC703", Hamlib.RIG_MODEL_IC703)
    ICOM_IC7800 = (SupportedManufacturer.ICOM, "IC7800", Hamlib.RIG_MODEL_IC7800)
    ICOM_IC756PROIII = (SupportedManufacturer.ICOM, "IC756PROIII", Hamlib.RIG_MODEL_IC756PROIII)
    ICOM_IC7000 = (SupportedManufacturer.ICOM, "IC7000", Hamlib.RIG_MODEL_IC7000)
    ICOM_IC7200 = (SupportedManufacturer.ICOM, "IC7200", Hamlib.RIG_MODEL_IC7200)
    ICOM_IC7700 = (SupportedManufacturer.ICOM, "IC7700", Hamlib.RIG_MODEL_IC7700)
    ICOM_IC7600 = (SupportedManufacturer.ICOM, "IC7600", Hamlib.RIG_MODEL_IC7600)
    ICOM_IC7410 = (SupportedManufacturer.ICOM, "IC7410", Hamlib.RIG_MODEL_IC7410)
    ICOM_IC9100 = (SupportedManufacturer.ICOM, "IC9100", Hamlib.RIG_MODEL_IC9100)
    ICOM_IC7100 = (SupportedManufacturer.ICOM, "IC7100", Hamlib.RIG_MODEL_IC7100)
    ICOM_IC7300 = (SupportedManufacturer.ICOM, "IC7300", Hamlib.RIG_MODEL_IC7300)
    ICOM_PERSEUS = (SupportedManufacturer.ICOM, "PERSEUS", Hamlib.RIG_MODEL_PERSEUS)
    ICOM_IC785x = (SupportedManufacturer.ICOM, "IC785x", Hamlib.RIG_MODEL_IC785x)
    ICOM_IC7610 = (SupportedManufacturer.ICOM, "IC7610", Hamlib.RIG_MODEL_IC7610)
    ICOM_IC9700 = (SupportedManufacturer.ICOM, "IC9700", Hamlib.RIG_MODEL_IC9700)
    ICOM_IC705 = (SupportedManufacturer.ICOM, "IC705", Hamlib.RIG_MODEL_IC705)
    TENTEC_CI_V_OMNIVI = (SupportedManufacturer.ICOM, "OMNIVI", Hamlib.RIG_MODEL_OMNIVI)
    TENTEC_CI_V_OMNIVIP = (SupportedManufacturer.ICOM, "OMNI-VI+", Hamlib.RIG_MODEL_OMNIVIP)
    TENTEC_CI_V_PARAGON2 = (SupportedManufacturer.ICOM, "PARAGON2", Hamlib.RIG_MODEL_PARAGON2)
    TENTEC_CI_V_DELTAII = (SupportedManufacturer.ICOM, "DELTAII", Hamlib.RIG_MODEL_DELTAII)
    TENTEC_TT550 = (SupportedManufacturer.TENTEC, "Pegasus", Hamlib.RIG_MODEL_TT550)
    TENTEC_TT538 = (SupportedManufacturer.TENTEC, "Jupiter", Hamlib.RIG_MODEL_TT538)
    TENTEC_TT526 = (SupportedManufacturer.TENTEC, "6N2", Hamlib.RIG_MODEL_TT526)
    TENTEC_TT516 = (SupportedManufacturer.TENTEC, "Argonaut", Hamlib.RIG_MODEL_TT516)
    TENTEC_TT565 = (SupportedManufacturer.TENTEC, "Orion", Hamlib.RIG_MODEL_TT565)
    TENTEC_TT585 = (SupportedManufacturer.TENTEC, "Paragon", Hamlib.RIG_MODEL_TT585)
    TENTEC_TT588 = (SupportedManufacturer.TENTEC, "Omni-VII", Hamlib.RIG_MODEL_TT588)
    TENTEC_TT599 = (SupportedManufacturer.TENTEC, "Eagle", Hamlib.RIG_MODEL_TT599)
    ALINCO_DX77 = (SupportedManufacturer.ALINCO, "DX77", Hamlib.RIG_MODEL_DX77)
    ALINCO_DXSR8 = (SupportedManufacturer.ALINCO, "DXSR8", Hamlib.RIG_MODEL_DXSR8)
    FLEXRADIO_SDR1000 = (SupportedManufacturer.FLEXRADIO, "SDR1000", Hamlib.RIG_MODEL_SDR1000)
    FLEXRADIO_SDR1000RFE = (SupportedManufacturer.FLEXRADIO, "SDR1000RFE", Hamlib.RIG_MODEL_SDR1000RFE)
    FLEXRADIO_DTTSP = (SupportedManufacturer.FLEXRADIO, "DTTSP", Hamlib.RIG_MODEL_DTTSP)
    FLEXRADIO_DTTSP_UDP = (SupportedManufacturer.FLEXRADIO, "DTTSP_UDP", Hamlib.RIG_MODEL_DTTSP_UDP)
    ADAT_ADT_200A = (SupportedManufacturer.ADAT, "ADT_200A", Hamlib.RIG_MODEL_ADT_200A)
  #  BARRETT_BARRETT_2050 = (SupportedManufacturer.BARRETT, "BARRETT_2050", Hamlib.RIG_MODEL_BARRETT_2050)
    ELAD_ELAD_FDM_DUO = (SupportedManufacturer.ELAD, "ELAD_FDM_DUO", Hamlib.RIG_MODEL_ELAD_FDM_DUO)

    def __init__(self, manufacturer, display_name, hamlib_rig_model=Hamlib.RIG_MODEL_TS480):
        self.manufacturer = manufacturer
        manufacturer.supportedRigs.append(self)
        self.displayName = display_name
        self.hamlibRigModel = hamlib_rig_model

    @classmethod
    def for_manufacturer_by_display_name(cls, manufacturer):
        return dict([(rig.displayName, rig) for rig in sorted(manufacturer.supportedRigs, key=lambda r: r.displayName)])


class ThreadSafeValue:
    def __init__(self,
                 exchange_value=multiprocessing.Value(ctypes.c_float),
                 exchange_value_timestamp=multiprocessing.Value(ctypes.c_int64, 0)  # very old timestamp, thus value seen invalid
                 ):
        self.exchangeValue = exchange_value
        self.exchangeValueTimestamp = exchange_value_timestamp

    def get(self, max_value_age_in_seconds):
        with self.exchangeValue.get_lock(), self.exchangeValueTimestamp.get_lock():
            if time.time_ns() - self.exchangeValueTimestamp.value <= max_value_age_in_seconds * 1000000000:
                return self.exchangeValue.value
            else:
                return None

    def set(self, value):
        with self.exchangeValue.get_lock(), self.exchangeValueTimestamp.get_lock():
            if value is None:
                self.exchangeValueTimestamp.value = 0  # very old timestamp, thus value seen invalid
            else:
                self.exchangeValue.value = value
                self.exchangeValueTimestamp.value = time.time_ns()


POLLING_INTERVAL_SECONDS = 0.4

SLEEP_SECONDS = 0.05


class CatPoller(multiprocessing.Process):

    def __init__(self, rig_data, thread_safe_value):
        exchange_do_stop = multiprocessing.Value(ctypes.c_bool, False)
        super().__init__(target=poll_frequency, args=(
            multiprocessing.Value(ctypes.c_int, rig_data["model"]),
            multiprocessing.Value(ctypes.c_int, rig_data["baud_rate"]),
            thread_safe_value.exchangeValue,
            thread_safe_value.exchangeValueTimestamp,
            exchange_do_stop,
        ), daemon=True)
        self.do_stop = exchange_do_stop

    def stop(self):
        self.do_stop.value = True
        while self.is_alive():
            time.sleep(SLEEP_SECONDS)


def poll_frequency(rig_model_value, baud_rate_value, exchange_value, exchange_value_timestamp, exchange_do_stop):
    hamlib_rig = init_rig(rig_model_value.value, baud_rate_value.value)
    thread_safe_value = ThreadSafeValue(exchange_value, exchange_value_timestamp)

    open_retrying(hamlib_rig, exchange_do_stop)

    while not exchange_do_stop.value:
        frequency = hamlib_rig.get_freq()
        log("poll_frequency: rig frequency " + str(frequency))
        if hamlib_rig.error_status != 0:
            log("WARNING: Error while getting frequency: %s" % Hamlib.rigerror(hamlib_rig.error_status))
            open_retrying(hamlib_rig, exchange_do_stop)
        elif not exchange_do_stop.value:
            thread_safe_value.set(frequency)

        stoppable_sleep(POLLING_INTERVAL_SECONDS, SLEEP_SECONDS, exchange_do_stop)

    hamlib_rig.close()
    if hamlib_rig.error_status != 0:
        log("WARNING: Error while closing device: %s" % Hamlib.rigerror(hamlib_rig.error_status))


def open_retrying(hamlib_rig, exchange_do_stop):
    while not exchange_do_stop.value:
        hamlib_rig.open()
        if hamlib_rig.error_status != 0:
            log("WARNING: Error while opening device: %s" % Hamlib.rigerror(hamlib_rig.error_status))
            stoppable_sleep(POLLING_INTERVAL_SECONDS, SLEEP_SECONDS, exchange_do_stop)
        else:
            break


def stoppable_sleep(total_time, interval, exchange_stop):
    sleep_time = 0
    while sleep_time < total_time and not exchange_stop.value:
        time.sleep(interval)
        sleep_time += interval


def test_frequency(test_hamlib_rig_data):
    if test_hamlib_rig_data is None:
        log("WARNING: no hamlib rig")
        return None
    test_hamlib_rig = init_rig(test_hamlib_rig_data["model"], test_hamlib_rig_data["baud_rate"])
    test_hamlib_rig.open()
    if test_hamlib_rig.error_status != 0:
        log("WARNING: Error while opening device: %s" % Hamlib.rigerror(test_hamlib_rig.error_status))
        return None
    frequency = test_hamlib_rig.get_freq()
    frequency_error_status = test_hamlib_rig.error_status
    if frequency_error_status != 0:
        log("WARNING: Error while getting frequency: %s" % Hamlib.rigerror(frequency_error_status))
    test_hamlib_rig.close()
    if test_hamlib_rig.error_status != 0:
        log("WARNING: Error while closing device: %s" % Hamlib.rigerror(test_hamlib_rig.error_status))
    if frequency_error_status == 0:
        return frequency
    else:
        return None


def init_rig(rig_model, baud_rate):
    hamlib_rig = Hamlib.Rig(rig_model)
    hamlib_rig.set_conf("rig_pathname",
                       "/dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.4:1.0-port0")
    hamlib_rig.set_conf("timeout", "50")  # TODO found a timeout!!
    hamlib_rig.set_conf("retry", "3")
    hamlib_rig.set_conf("serial_speed", str(baud_rate))
    return hamlib_rig


class CATInterface:

    def __init__(self, operational_interface_control):
        self.operationalInterfaceControl = operational_interface_control
        Hamlib.rig_set_debug(Hamlib.RIG_DEBUG_NONE)
        self.threadSafeValue = ThreadSafeValue()
        self.rigData = None
        self.pollerProcess = None
        self.isOpen = False
        self.init_rig_data_if_configured()

    def init_rig_data_if_configured(self):
        cat_config = Config.get_instance().catConfig
        saved_rig_model = None if cat_config["rig"] is None else SupportedRig[cat_config["rig"]]
        saved_baud_rate = cat_config["baud_rate"]
        if saved_rig_model is not None and saved_baud_rate is not None:
            self.rigData = {"model": saved_rig_model.hamlibRigModel, "baud_rate": saved_baud_rate}

    def test_rig_and_baud_rate(self, rig, baud_rate):
        was_open = self.isOpen
        if was_open:
            self.stop_poller()
        test_hamlib_rig = {"model": rig.hamlibRigModel, "baud_rate": baud_rate}
        frq = test_frequency(test_hamlib_rig)
        if was_open:
            self.start_poller()
        return frq

    def set_rig_and_baud_rate(self, rig, baud_rate):
        was_open = self.isOpen
        if was_open:
            self.stop_poller()
        self.rigData = {"model": rig.hamlibRigModel, "baud_rate": baud_rate}
        if was_open:
            self.start_poller()

    def get_frequency(self):
        return self.threadSafeValue.get(4)

    def reset_frequency(self):
        self.threadSafeValue.set(None)

    def start_poller(self):
        self.isOpen = True
        if self.pollerProcess is None:
            self.pollerProcess = CatPoller(self.rigData, self.threadSafeValue)
        self.pollerProcess.start()

    def stop_poller(self):
        self.isOpen = False
        if self.pollerProcess is not None and self.pollerProcess.is_alive():
            self.pollerProcess.stop()
        self.pollerProcess = None

    def is_configured(self):
        return self.rigData is not None
