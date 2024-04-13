from abc import ABC
from enum import Enum

from config import Config
from interface import InterfaceWrapper


class PowerSupplyDataSource(Enum):
    DEFAULT = 0
    CAN = 1
    CAN_FROM_CONTROLLER = 2


class CanConnectorABC(ABC):
    def start_receiving(self):
        pass

    def stop_receiving(self):
        pass

    def initialize_power_supply(self):
        voltage_limit_in_volt = Config.get_instance().canPower.get("voltage")
        self.set_nominal_voltage(voltage_limit_in_volt)

        self.initialize_current_limits()

    def set_nominal_voltage(self, voltage_limit_in_volt):
        pass

    def initialize_current_limits(self):
        pass


class CanConnectorFactory:
    connectorInstance = None

    @classmethod
    def get_can_connector_instance(cls) -> CanConnectorABC:
        if cls.connectorInstance is None:
            power_supply_data_source = PowerSupplyDataSource(
                InterfaceWrapper.getInstance().get_power_supply_data_source())
            if power_supply_data_source == PowerSupplyDataSource.CAN:
                from canBus.directCanConnector import DirectCanConnector
                cls.connectorInstance = DirectCanConnector()
            elif power_supply_data_source == PowerSupplyDataSource.CAN_FROM_CONTROLLER:
                cls.connectorInstance = ControllerCanConnector()
            else:
                cls.connectorInstance = DummyCanConnector()
        return cls.connectorInstance


class DummyCanConnector(CanConnectorABC):
    def start_receiving(self):
        pass

    def stop_receiving(self):
        pass

    def initialize_power_supply(self):
        pass


class ControllerCanConnector(CanConnectorABC):

    def set_nominal_voltage(self, voltage_limit_in_volt):
        InterfaceWrapper.getInstance().set_nominal_power_supply_voltage(voltage_limit_in_volt)

    def initialize_current_limits(self):
        InterfaceWrapper.getInstance().initialize_power_supply_current_limits()
