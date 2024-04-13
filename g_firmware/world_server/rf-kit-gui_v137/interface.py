import multiprocessing
import traceback
from queue import Empty
from threading import Lock
from tkinter import StringVar

from customlogging import log

from simple_rpc import Interface
import time
import os

from debug.debugCalibrationEnums import DebugCalibrationType, Band


class Request:
    def __init__(self, method_name, *args):
        self.method_name = method_name
        self.arguments = args

    def __str__(self):
        return self.method_name + "(" + str(self.arguments) + ")"


class InterfaceProcess(multiprocessing.Process):
    @classmethod
    def interface_proccess_loop(cls, device, baud_rate, request_queue, response_queue, ready_event,
                                shutdown_requested_event):
        log("started process loop")
        try:
            with Interface(device, baud_rate) as real_interface:
                log("initialized interface in process")
                ready_event.set()
                while True:
                    if shutdown_requested_event.is_set():
                        log("terminate request received")
                        break
                    request = request_queue.get()
                    if request is not None:
                        interface_method = getattr(real_interface, request.method_name)
                        response = interface_method(*request.arguments)
                        response_queue.put(response)
        except:
            log("ERROR: error in interface process loop: " + traceback.format_exc())
        log("end of interface process loop")

    def __init__(self, device, baud_rate, request_queue, response_queue, start_timeout_seconds):
        ready_event = multiprocessing.Event()
        shutdown_requested_event = multiprocessing.Event()
        super().__init__(target=InterfaceProcess.interface_proccess_loop,
                         args=(device, baud_rate, request_queue, response_queue, ready_event, shutdown_requested_event),
                         daemon=True)
        self.requestQueue = request_queue
        self.ready = ready_event
        self.shutdownRequested = shutdown_requested_event
        self.startTimoutSeconds = start_timeout_seconds

    def start(self):
        super().start()
        is_ready = self.ready.wait(timeout=self.startTimoutSeconds)
        if not is_ready:
            raise InterfaceException(
                "interface process was not ready after " + str(self.startTimoutSeconds) + " seconds")

    def request_graceful_shutdown(self):
        log("sending terminate request to interface process")
        self.shutdownRequested.set()
        self.requestQueue.put(None)
        log("terminate request sent to interface process")


class InterfaceException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InterfaceWrapper:
    instance = None

    @classmethod
    def getInstance(cls):
        if cls.instance is None:
            cls.instance = InterfaceWrapper(
                '/dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.3:1.0-port0', 115200, 30, 5, 10, 5)
        return cls.instance

    def __init__(self, device, baudrate, timeout_seconds, start_timeout_seconds, restart_sleep_seconds,
                 grace_period_seconds):
        self.device = device
        self.baudrate = baudrate
        self.timeoutSeconds = timeout_seconds
        self.startTimoutSeconds = start_timeout_seconds
        self.restartSleepSeconds = restart_sleep_seconds
        self.gracePeriodSeconds = grace_period_seconds
        self.errorStringVar = StringVar()
        self.requests = multiprocessing.Queue(maxsize=1)
        self.responses = multiprocessing.Queue(maxsize=1)
        self.interfaceProcess = None
        self.mutex = Lock()
        self.mutex.acquire()
        self._init_process()
        self.mutex.release()

    def _init_process(self):
        self.interfaceProcess = InterfaceProcess(self.device, self.baudrate, self.requests, self.responses,
                                                 self.startTimoutSeconds)
        try:
            self.interfaceProcess.start()
        except:
            log("ERROR: error starting interface process: " + traceback.format_exc())
            self._replace_process()

    def _set_error(self, message):
        self.errorStringVar.set(message)
        self.errorStringVar._root.update_idletasks()

    def _reset_error(self):
        self._set_error("")

    def _replace_process(self):
        self._set_error("Restarting serial interface...")
        log("replacing interface process...")
        self.interfaceProcess.kill()
        timestamp_after_kill = time.monotonic()
        while True:
            try:
                self.requests.get(
                    timeout=self.restartSleepSeconds / 2.0)  # wait as long as we can afford without exceeding configured sleep time (queue capacity is 1)
            except Empty:
                break
        while True:
            try:
                self.responses.get(timeout=self.restartSleepSeconds / 2.0)
            except Empty:
                break
        remaining_sleep_seconds = self.restartSleepSeconds - (time.monotonic() - timestamp_after_kill)
        if remaining_sleep_seconds > 0:
            time.sleep(remaining_sleep_seconds)  # sleep only rest of restartSleepSeconds
        log("interface process killed")
        self._init_process()
        log("interface process initialized")
        self._reset_error()

    def _run_in_process(self, interface_method_name, *args, no_timeout=False, external_mutex=False):
        timeout = None if no_timeout else self.timeoutSeconds
        if not external_mutex:
            self.mutex.acquire()

        self.requests.put(Request(interface_method_name, *args))
        try:
            resp = self.responses.get(timeout=timeout)
            return resp
        except Empty:
            self._replace_process()
            raise InterfaceException("Timeout during reading from interface")
        except BaseException as e:
            log("ERROR: error while getting response from queue: " + traceback.format_exc())
            raise InterfaceException(str(e))
        except:
            log("ERROR: error while getting response from queue " + traceback.format_exc())
            raise InterfaceException("unknown error while getting response from queue")
        finally:
            if not external_mutex:
                self.mutex.release()

    def close(self):
        if self.mutex.acquire(timeout=self.timeoutSeconds):
            try:
                self.interfaceProcess.request_graceful_shutdown()
                self.interfaceProcess.join(timeout=self.gracePeriodSeconds)
            finally:
                self.mutex.release()
        if self.interfaceProcess.is_alive():
            self.interfaceProcess.kill()

    def display_on(self):
        self._run_in_process("set_display", 1)

    def display_off(self):
        self._run_in_process("set_display", 0)

    def go_sleep(self):
        self._run_in_process("go_sleep")

    def wake_up(self):
        self._run_in_process("wake_up")

    def get_tuner_on_off_per_band(self):
        return self._run_in_process("get_tuner_on_off_per_band")

    def set_tuner_on_off_for_band(self, band_index, on):
        self._run_in_process("set_tuner_on_off_for_band", band_index, on)

    def set_operate(self):
        self._run_in_process("set_operate")

    def get_offset_BIAS(self):
        return self._run_in_process("get_offset_BIAS")

    def get_storage_bank(self):
        return self._run_in_process("get_storage_bank")

    def get_default_antennas(self):
        return self._run_in_process("get_default_antennas")

    def get_ext_antenna_high_low_active(self):
        return self._run_in_process("get_bcd_active")

    def set_ext_antenna_high_low_active(self, high):
        self._run_in_process("set_bcd_active", high)

    def set_use_ext_antenna(self, use_ext):
        self._run_in_process("set_ant_output", use_ext)

    def get_power_supply_data_source(self):
        return self._run_in_process("get_power_supply_data_source")

    def set_power_supply_voltage(self, voltage):
        self._run_in_process("set_power_supply_voltage", voltage)

    def set_power_supply_current(self, current):
        self._run_in_process("set_power_supply_current", current)

    def get_all_values(self):
        return self._run_in_process("get_all_values")

    def set_standby(self):
        self._run_in_process("set_standby")

    def set_tuner_auto(self, mode):
        mode_interface_arg = 1 if mode else 0
        self._run_in_process("set_tuner_auto", mode_interface_arg)

    def set_tuner_bypass(self, state):
        self._run_in_process("set_tuner_bypass", state)

    def set_K(self, state):
        self._run_in_process("set_K", state)

    def set_antenna(self, number):
        self._run_in_process("set_antenna", number)

    def set_default_antenna(self, filter, antenna):
        self._run_in_process("set_default_antenna", filter, antenna)

    def set_storage_bank(self, bank):
        self._run_in_process("set_storage_bank", bank)

    def delete_storage(self, num):
        self._run_in_process("delete_storage", num)

    def delete_tuner_antenna(self, num):
        self._run_in_process("delete_tuner_antenna", num)

    def delete_tuner_ext_antenna(self, num):
        self._run_in_process("delete_tuner_ext_antenna", num)

    def autotune(self):
        self._run_in_process("autotune")

    def autotune_full(self):
        self._run_in_process("autotune_full")

    def increment_L(self, steps):
        self._run_in_process("increment_L", steps)

    def decrement_L(self, steps):
        self._run_in_process("decrement_L", steps)

    def increment_C(self, steps):
        self._run_in_process("increment_C", steps)

    def decrement_C(self, steps):
        self._run_in_process("decrement_C", steps)

    def store_tuner(self):
        self._run_in_process("store_tuner")

    def store_config(self):
        self._run_in_process("store_config")

    def reset_tuner(self):
        self._run_in_process("reset_tuner")

    def reset_error_state(self):
        self._run_in_process("reset_error_state")

    def increment_offset_F(self):
        self._run_in_process("increment_offset_F")

    def decrement_offset_F(self):
        self._run_in_process("decrement_offset_F")

    def increment_offset_R(self):
        self._run_in_process("increment_offset_R")

    def decrement_offset_R(self):
        self._run_in_process("decrement_offset_R")

    def increment_offset_BIAS(self):
        self._run_in_process("increment_offset_BIAS")

    def decrement_offset_BIAS(self):
        self._run_in_process("decrement_offset_BIAS")

    def zeroFRAM(self):
        self._run_in_process("zeroFRAM")

    def isTunerAtSixMeterEnabled(self):
        return self._run_in_process("get_tuner_6m_setting")

    def setTunerAtSixMeterEnabled(self, setting):
        self._run_in_process("set_tuner_6m_setting", setting)

    def getHighLowPower(self):
        return self._run_in_process("get_PE5")

    def setHighLowPower(self, one_if_high_zero_if_low):
        self._run_in_process("set_PE5", one_if_high_zero_if_low)

    def get_frq_count(self):
        return self._run_in_process("get_frq_count")

    def incr_frq_count(self):
        self._run_in_process("incr_frq_count")

    def decr_frq_count(self):
        self._run_in_process("decr_frq_count")

    def set_operational_interface(self, op_i):
        self._run_in_process("set_operational_interface", op_i)

    def set_cat_frq(self, cat_frq):
        self._run_in_process("set_cat_frq", cat_frq)

    def get_dac_offset(self, debug_calibration_type: DebugCalibrationType, band: Band):
        method_for_type = None
        if debug_calibration_type is DebugCalibrationType.BIAS:
            method_for_type = "get_dac_value_bias"
        elif debug_calibration_type is DebugCalibrationType.INPUT:
            method_for_type = "get_dac_value_input"
        else:  # INPUT_OFFSET
            method_for_type = "get_dac_offset_input"
        argument = band.enumValue
        return self._run_in_process(method_for_type, argument)

    def increment_dac_offset(self, debug_calibration_type: DebugCalibrationType, band: Band):
        method_for_type = None
        if debug_calibration_type is DebugCalibrationType.BIAS:
            method_for_type = "increment_dac_value_bias"
        elif debug_calibration_type is DebugCalibrationType.INPUT:
            method_for_type = "increment_dac_value_input"
        else:  # INPUT_OFFSET
            method_for_type = "increment_dac_offset_input"
        argument = band.enumValue
        self._run_in_process(method_for_type, argument)

    def decrement_dac_offset(self, debug_calibration_type: DebugCalibrationType, band: Band):
        method_for_type = None
        if debug_calibration_type is DebugCalibrationType.BIAS:
            method_for_type = "decrement_dac_value_bias"
        elif debug_calibration_type is DebugCalibrationType.INPUT:
            method_for_type = "decrement_dac_value_input"
        else:  # INPUT_OFFSET
            method_for_type = "decrement_dac_offset_input"
        argument = band.enumValue
        self._run_in_process(method_for_type, argument)

    def get_generation(self):
        return self._run_in_process("get_generation")

    def get_high_current_threshold(self):
        return self._run_in_process("get_high_current_threshold")

    def update(self, filepath, progress_callback):
        self.mutex.acquire()
        try:
            buffer_len = 1024
            self._run_in_process("start_update", no_timeout=True, external_mutex=True)
            print("sleep")
            for i in range(1, 11):
                time.sleep(1)
                progress_callback(0.2 * (i / 10))
            with open(filepath, "rb") as f:
                filesize = os.fstat(f.fileno()).st_size
                transferred_bytes = 0
                segment = 0
                error_counter = 0
                data = f.read(buffer_len)
                while data:
                    data_list = list(bytes([r]) for r in data)
                    result = self._run_in_process("send_segment", segment, data_list, no_timeout=True,
                                                  external_mutex=True)
                    if data_list == result:
                        segment = segment + 1
                        data = f.read(buffer_len)
                        error_counter = 0
                        transferred_bytes += len(data_list)
                        progress_callback(0.2 + 0.8 * (transferred_bytes / filesize))
                    else:
                        print("segment not equal")
                        error_counter = error_counter + 1
                        if error_counter == 10:
                            break
                if error_counter < 10:
                    self._run_in_process("flash", no_timeout=True, external_mutex=True)
                else:
                    print(
                        "Error flashing microcontroller. Try again. If this error does appear again, contact support.")
        finally:
            self.mutex.release()
