from threading import Lock

from simple_rpc import Interface
import time
import os

# move to programm start
interface = Interface('/dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.3:1.0-port0', 115200)  # set correct device
from debug.debugCalibrationEnums import DebugCalibrationType, Band

mutex = Lock()

def close():
    mutex.acquire()
    try:
        interface.close()
    finally:
        mutex.release()

def get_version():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_version()
    finally:
        mutex.release()

def display_on():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.set_display(1)
    finally:
        mutex.release()

def display_off():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.set_display(0)
    finally:
        mutex.release()


def go_sleep():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.go_sleep()
    finally:
        mutex.release()

def wake_up():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.wake_up()
    finally:
        mutex.release()

def get_tuner_on_off_per_band():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_tuner_on_off_per_band()
    finally:
        mutex.release()

def set_tuner_on_off_for_band(band_index, on):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.set_tuner_on_off_for_band(band_index, on)
    finally:
        mutex.release()

def is_calibrated():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.is_calibrated()
    finally:
        mutex.release()


def get_voltage():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_voltage()
    finally:
        mutex.release()


def get_current():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_current()
    finally:
        mutex.release()


def get_temperature():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_temperature()
    finally:
        mutex.release()


def get_max_digits_value():
    return 4096


def get_P_F():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_P_F()
    finally:
        mutex.release()


def get_P_dF():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_P_dF()
    finally:
        mutex.release()


def get_P_AF():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.getP_AF()
    finally:
        mutex.release()


def get_P_dAF():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.getP_dAF()
    finally:
        mutex.release()


def get_P_R():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_P_R()
    finally:
        mutex.release()


def get_P_dR():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_P_dR()
    finally:
        mutex.release()


def get_SWR():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_SWR()
    finally:
        mutex.release()


def get_F_m():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_F_m()
    finally:
        mutex.release()


def get_filter():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_filter()
    finally:
        mutex.release()


def get_F_t():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_F_t()
    finally:
        mutex.release()


def get_L():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_L()
    finally:
        mutex.release()


def get_C():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_C()
    finally:
        mutex.release()


def is_tuner_bypass_set():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.is_tuner_bypass_set()
    finally:
        mutex.release()


def get_K():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_K()
    finally:
        mutex.release()


def is_PTT_set():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.is_PTT_set()
    finally:
        mutex.release()


def is_BIAS_set():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.is_BIAS_set()
    finally:
        mutex.release()


def set_operate():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.set_operate()
    finally:
        mutex.release()


def get_offset():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_offset()
    finally:
        mutex.release()


def get_offset_BIAS():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_offset_BIAS()
    finally:
        mutex.release()


def get_storage_bank():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_storage_bank()
    finally:
        mutex.release()


def get_default_antennas():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_default_antennas()
    finally:
        mutex.release()


def get_ext_antenna_high_low_active():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.get_bcd_active()
    finally:
        mutex.release()


def set_ext_antenna_high_low_active(high):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.set_bcd_active(high)
    finally:
        mutex.release()

def set_use_ext_antenna(use_ext):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.set_ant_output(use_ext)
    finally:
        mutex.release()


def get_power_supply_data_source():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_power_supply_data_source()
    finally:
        mutex.release()


def set_power_supply_voltage(voltage):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.set_power_supply_voltage(voltage)
    finally:
        mutex.release()


def set_power_supply_current(current):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.set_power_supply_current(current)
    finally:
        mutex.release()


def get_all_values():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_all_values()
    finally:
        mutex.release()


def set_standby():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.set_standby()
    finally:
        mutex.release()


def set_tuner_auto(mode):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.set_tuner_auto(1 if mode else 0)
    finally:
        mutex.release()


def set_tuner_bypass(state):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.set_tuner_bypass(state)
    finally:
        mutex.release()


def set_K(state):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.set_K(state)
    finally:
        mutex.release()


def set_antenna(number):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.set_antenna(number)
    finally:
        mutex.release()


def set_default_antenna(filter, antenna):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.set_default_antenna(filter, antenna)
    finally:
        mutex.release()


def set_storage_bank(bank):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.set_storage_bank(bank)
    finally:
        mutex.release()


def delete_storage(num):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.delete_storage(num)
    finally:
        mutex.release()


def delete_tuner_antenna(num):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.delete_tuner_antenna(num)
    finally:
        mutex.release()

def delete_tuner_ext_antenna(num):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.delete_tuner_ext_antenna(num)
    finally:
        mutex.release()

def autotune():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.autotune()
    finally:
        mutex.release()

def autotune_full():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.autotune_full()
    finally:
        mutex.release()

def increment_L(steps):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.increment_L(steps)
    finally:
        mutex.release()


def decrement_L(steps):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.decrement_L(steps)
    finally:
        mutex.release()


def increment_C(steps):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.increment_C(steps)
    finally:
        mutex.release()


def decrement_C(number):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.decrement_C(number)
    finally:
        mutex.release()


def store_tuner():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.store_tuner()
    finally:
        mutex.release()


def store_config():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.store_config()
    finally:
        mutex.release()


def reset_tuner():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.reset_tuner()
    finally:
        mutex.release()


def reset_error_state():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.reset_error_state()
    finally:
        mutex.release()


def increment_offset_F():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.increment_offset_F()
    finally:
        mutex.release()


def decrement_offset_F():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.decrement_offset_F()
    finally:
        mutex.release()


def increment_offset_R():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.increment_offset_R()
    finally:
        mutex.release()


def decrement_offset_R():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.decrement_offset_R()
    finally:
        mutex.release()


def increment_offset_BIAS():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.increment_offset_BIAS()
    finally:
        mutex.release()


def decrement_offset_BIAS():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.decrement_offset_BIAS()
    finally:
        mutex.release()


def zeroFRAM():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.zeroFRAM()
    finally:
        mutex.release()

def isTunerAtSixMeterEnabled():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_tuner_6m_setting()
    finally:
        mutex.release()

def setTunerAtSixMeterEnabled(setting):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.set_tuner_6m_setting(setting)
    finally:
        mutex.release()

def getHighLowPower():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_PE5()
    finally:
        mutex.release()


def setHighLowPower(oneIfHighZeroIfLow):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.set_PE5(oneIfHighZeroIfLow)
    finally:
        mutex.release()

def get_frq_count():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_frq_count()
    finally:
        mutex.release()


def incr_frq_count():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.incr_frq_count()
    finally:
        mutex.release()


def decr_frq_count():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.decr_frq_count()
    finally:
        mutex.release()

def set_operational_interface(op_i):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.set_operational_interface(op_i)
    finally:
        mutex.release()

def set_cat_frq(cat_frq):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        interface.set_cat_frq(cat_frq)
    finally:
        mutex.release()


def get_dac_offset(debug_calibration_type: DebugCalibrationType, band: Band):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        if debug_calibration_type is DebugCalibrationType.BIAS:
            return interface.get_dac_value_bias(band.enumValue)
        elif debug_calibration_type is DebugCalibrationType.INPUT:
            return interface.get_dac_value_input(band.enumValue)
        else:  #INPUT_OFFSET
            return interface.get_dac_offset_input(band.enumValue)
    finally:
        mutex.release()

def increment_dac_offset(debug_calibration_type: DebugCalibrationType, band: Band):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        if debug_calibration_type is DebugCalibrationType.BIAS:
            interface.increment_dac_value_bias(band.enumValue)
        elif debug_calibration_type is DebugCalibrationType.INPUT:
            interface.increment_dac_value_input(band.enumValue)
        else:  #INPUT_OFFSET
            interface.increment_dac_offset_input(band.enumValue)
    finally:
        mutex.release()

def decrement_dac_offset(debug_calibration_type: DebugCalibrationType, band: Band):
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        if debug_calibration_type is DebugCalibrationType.BIAS:
            interface.decrement_dac_value_bias(band.enumValue)
        elif debug_calibration_type is DebugCalibrationType.INPUT:
            interface.decrement_dac_value_input(band.enumValue)
        else:  #INPUT_OFFSET
            interface.decrement_dac_offset_input(band.enumValue)
    finally:
        mutex.release()

def update(filepath, progressCallback):
    mutex.acquire()
    try:
        buffer_len = 1024
        if not interface.is_open():
            interface.open()
        interface.start_update()
        print("sleep")
        for i in range(1, 11):
            time.sleep(1)
            progressCallback(0.2 * (i / 10))
        with open(filepath, "rb") as f:
            filesize = os.fstat(f.fileno()).st_size
            transferredBytes = 0
            segment = 0
            error_counter = 0
            data = f.read(buffer_len)
            while data:
                data_list = list(bytes([r]) for r in data)
                result = interface.send_segment(segment, data_list)
                if data_list == result:
                    segment = segment + 1
                    data = f.read(buffer_len)
                    error_counter = 0
                    transferredBytes += len(data_list)
                    progressCallback(0.2 + 0.8 * (transferredBytes / filesize))
                else:
                    print("segment not equal")
                    error_counter = error_counter + 1
                    if error_counter == 10:
                        break
            if error_counter < 10:
                interface.flash()
            else:
                print("Error flashing microcontroller. Try again. If this error does appear again, contact support.")
    finally:
        mutex.release()

def get_generation():
    mutex.acquire()
    try:
        if not interface.is_open():
            interface.open()
        return interface.get_generation()
    finally:
        mutex.release()
