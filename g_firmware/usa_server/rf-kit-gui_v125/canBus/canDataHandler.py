import can
import interface
from canBus.canHelper import extract_value


class CanDataHandler(can.Listener):

    def on_message_received(self, msg):
        data = msg.data
        if (data[0] == 0x01 and data[1] == 0x75):
            interface.set_power_supply_voltage(extract_value(data) / 1024)

        if (data[0] == 0x01 and data[1] == 0x81):
            interface.set_power_supply_current(extract_value(data) / 1024)
