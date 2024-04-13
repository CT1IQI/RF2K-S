import os

from customlogging import log
from network.networkConfigElements import DhcpConfigElement, uncomment, STATIC_CONF_PART

NETWORK_CONFIG_PATH = "/etc/dhcpcd.conf"

LAN_HEADING = "interface eth0\n"
WLAN_HEADING = "interface wlan0\n"

class NetworkConfig:
    instance = None


    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            #load config
            cls.instance = NetworkConfig()
        return cls.instance

    def __init__(self):
        self.lanDhcp = DhcpConfigElement(self.extract_lan_lines())
        self.wlanDhcp = DhcpConfigElement(self.extract_wlan_lines())

    def save_and_apply_LAN(self):
        wlan_lines = self.extract_wlan_lines()

        with open(NETWORK_CONFIG_PATH, "w") as network_config_file:
            network_config_file.write(STATIC_CONF_PART)
            network_config_file.writelines(self.lanDhcp.toLines(LAN_HEADING))
            network_config_file.writelines(wlan_lines)

        os.system('sync')
        ret_val = os.system('sudo ifconfig eth0 down && sudo ifconfig eth0 up')
        if ret_val != 0:
            log("error restarting eth0")

    def save_WLAN(self):
        lan_lines = self.extract_lan_lines()

        with open(NETWORK_CONFIG_PATH, "w") as network_config_file:
            network_config_file.write(STATIC_CONF_PART)
            network_config_file.writelines(lan_lines)
            network_config_file.writelines(self.wlanDhcp.toLines(WLAN_HEADING))

        os.system('sync')

    def reset_LAN(self):
        self.lanDhcp.reset()
        self.save_and_apply_LAN()

    def reset_WLAN(self):
        self.wlanDhcp.reset()
        self.save_WLAN()

    def extract_lan_lines(self):
        return self.extract_lines(LAN_HEADING, WLAN_HEADING)

    def extract_wlan_lines(self):
        return self.extract_lines(WLAN_HEADING)

    def extract_lines(self, start_line_incl, end_line_excl=None):
        lines = []
        select = False
        with open(NETWORK_CONFIG_PATH) as network_config_file:
            for line in network_config_file:
                if uncomment(line) == start_line_incl:
                    select = True
                if uncomment(line) == end_line_excl:
                    break
                if select:
                    lines.append(line)
        return lines
