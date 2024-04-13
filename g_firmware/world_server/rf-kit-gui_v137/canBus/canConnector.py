import can  # needs package python-can
from canBus.canDataHandler import CanDataHandler
from canBus.canHelper import convert_to_message_data
from config import Config

SETTER_ARBITRATION_ID = 0x108180FE


class CanConnector:
    def __init__(self):
        self.filters = [
            {"can_id": 0x1081407F, "can_mask": 0x1FFFFFFF, "extended": True},
        ]
        self.bus = can.ThreadSafeBus(channel="can0", bustype="socketcan", can_filters=self.filters)
        self.sendTask = None

    def start_receiving(self):
        msg = can.Message(arbitration_id=0x108040FE, data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                          is_extended_id=True)

        handler = CanDataHandler()
        can.Notifier(self.bus, [handler])

        self.sendTask = self.bus.send_periodic(msg, 0.20)

    def stop_receiving(self):
        self.sendTask.stop()
        self.sendTask = None

    def initialize_power_supply(self):
        # set on-line output voltage
        voltage_limit_in_volt = Config.get_instance().canPower.get("voltage")
        self.set_value([0x01, 0x00, 0x00, 0x00], voltage_limit_in_volt * 1024)

        current_limit_in_unknown_unit = 1129
        # set on-line current limit
        self.set_value([0x01, 0x03, 0x00, 0x00], current_limit_in_unknown_unit)
        # set off-line/default current limit
        self.set_value([0x01, 0x04, 0x00, 0x00], current_limit_in_unknown_unit)

    def set_value(self, key_bytes, value):
        msg = can.Message(arbitration_id=SETTER_ARBITRATION_ID,
                          data=convert_to_message_data(key_bytes, value),
                          is_extended_id=True)
        self.bus.send(msg)

