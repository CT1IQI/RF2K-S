from enum import Enum

from interface import InterfaceWrapper


class PowerSupplyDataSource(Enum):
    DEFAULT = 0
    CAN = 1


class CanConnectorFactory:
    connectorInstance = None

    @classmethod
    def get_can_connector_instance(cls):
        if cls.connectorInstance is None:
            if PowerSupplyDataSource(InterfaceWrapper.getInstance().get_power_supply_data_source()) == PowerSupplyDataSource.CAN:
                from canBus.canConnector import CanConnector
                cls.connectorInstance = CanConnector()
            else:
                cls.connectorInstance = DummyCanConnector()
        return cls.connectorInstance


class DummyCanConnector:
    def start_receiving(self):
        pass

    def stop_receiving(self):
        pass

    def initialize_power_supply(self):
        pass