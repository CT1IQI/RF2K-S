import time
from multiprocessing import Lock

import can

from customlogging import log
from interface import InterfaceWrapper, InterfaceException
from canBus.canHelper import extract_value


class CanDataHandler(can.Listener):
    class ValueUpdater:

        def __init__(self, setter, min_value_difference=0.1, min_interval_ms=200, critical_value_test=None):
            self.setter = setter
            self.minValueDifference = min_value_difference
            self.minIntervalMs = min_interval_ms
            self.criticalValueTest = critical_value_test
            self.lastSendTimestampNs = None
            self.lastSentValue = None
            self.lastCriticalSentTimestampNs = None
            self.lock = Lock()

        def update_value(self, value):
            with self.lock:
                current_ts_ns = time.monotonic_ns()
                if value is not None:
                    if self.is_critical(value) and self.is_interval_long_enough(current_ts_ns, True):
                        self.setter(value)
                        self.lastSentValue = value
                        self.lastSendTimestampNs = current_ts_ns
                        self.lastCriticalSentTimestampNs = current_ts_ns
                    elif self.is_interval_long_enough(current_ts_ns,
                                                      False) and self.is_different_enough_from_last_value(value):
                        self.setter(value)
                        self.lastSentValue = value
                        self.lastSendTimestampNs = current_ts_ns

        def is_critical(self, value):
            return self.criticalValueTest is not None and self.criticalValueTest(value)

        def is_interval_long_enough(self, current_ts_ns, critical):
            relevant_last_timestamp = self.lastCriticalSentTimestampNs if critical else self.lastSendTimestampNs
            return relevant_last_timestamp is None or current_ts_ns - relevant_last_timestamp >= self.minIntervalMs * 1000000

        def is_different_enough_from_last_value(self, value):
            return self.lastSentValue is None or abs(self.lastSentValue - value) > self.minValueDifference

    def __init__(self):
        super().__init__()
        high_current_threshold = InterfaceWrapper.getInstance().get_high_current_threshold()
        self.voltageUpdater = CanDataHandler.ValueUpdater(InterfaceWrapper.getInstance().set_power_supply_voltage)
        self.currentUpdater = CanDataHandler.ValueUpdater(InterfaceWrapper.getInstance().set_power_supply_current,
                                                          critical_value_test=lambda
                                                              current: current >= high_current_threshold)

    def on_message_received(self, msg):
        data = msg.data
        if data[0] == 0x01 and data[1] == 0x75:
            voltage = extract_value(data) / 1024
            try:
                self.voltageUpdater.update_value(voltage)
            except InterfaceException as e:
                log("WARNING: interface error while sending voltage: " + str(e))

        if data[0] == 0x01 and data[1] == 0x81:
            current = extract_value(data) / 1024
            try:
                self.currentUpdater.update_value(current)
            except InterfaceException as e:
                log("WARNING: interface error while sending current: " + str(e))
