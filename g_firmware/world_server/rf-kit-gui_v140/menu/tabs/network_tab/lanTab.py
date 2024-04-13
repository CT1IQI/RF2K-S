from menu.tabs.network_tab.abstractNetworkTab import AbstractNetworkTab
from network.networkConfig import NetworkConfig


class LanTab(AbstractNetworkTab):
    def __init__(self, delegate, container):
        super(LanTab, self).__init__(delegate, container)

    def getDhcpConfig(self):
        return NetworkConfig.get_instance().lanDhcp

    def on_save_and_apply_clicked(self):
        NetworkConfig.get_instance().save_and_apply_LAN()

    def restore_default(self):
        NetworkConfig.get_instance().reset_LAN()

    def get_interface_name(self):
        return "eth0"
