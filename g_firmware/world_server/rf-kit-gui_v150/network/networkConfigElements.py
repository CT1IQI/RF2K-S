from tkinter import BooleanVar, StringVar


STATIC_CONF_PART = """# Inform the DHCP server of our hostname for DDNS.
hostname

# Use the hardware address of the interface for the Client ID.
clientid

# Persist interface configuration when dhcpcd exits.
persistent

# Rapid commit support.
# Safe to enable by default because it requires the equivalent option set
# on the server to actually work.
option rapid_commit

# A list of options to request from the DHCP server.
option domain_name_servers, domain_name, domain_search, host_name
option classless_static_routes
# Respect the network MTU. This is applied to DHCP routes.
option interface_mtu

# A ServerID is required by RFC2131.
require dhcp_server_identifier

# generate Stable Private IPv6 Addresses based from the DUID
slaac private

# manual dhcp configurations

"""

MANUAL_IP_ADDRESS_KEY = "static ip_address"
MANUAL_ROUTER_KEY = "static routers"
MANUAL_NAME_SERVER_KEY = "static domain_name_servers"


def is_commented(line):
    return line.strip().startswith('#')

def uncomment(line):
    return line.strip('# ')

def contains_value(line, key):
    return uncomment(line).startswith(key + '=')

def get_value(line, key):
    return uncomment(line).split(key + '=', 1)[1].strip()


class DhcpConfigElement:

    def __init__(self, config_lines):
        self.manual = BooleanVar(value=False)
        self.manualIpAdress = StringVar()
        self.manualRouter = StringVar()
        self.manualNameServer = StringVar()
        self.load_network_config(config_lines)

    def load_network_config(self, config_lines):
        manualIpAdressConfigured = False
        manualRouterConfigured = False
        manualNameServerConfigured = False
        for line in config_lines:
            if contains_value(line, MANUAL_IP_ADDRESS_KEY):
                value = get_value(line, MANUAL_IP_ADDRESS_KEY)
                if not is_commented(line):
                    self.manualIpAdress.set(value)
                    manualIpAdressConfigured = True
                elif not manualIpAdressConfigured:
                    self.manualIpAdress.set(value)
            elif contains_value(line, MANUAL_ROUTER_KEY):
                value = get_value(line, MANUAL_ROUTER_KEY)
                if not is_commented(line):
                    self.manualRouter.set(value)
                    manualRouterConfigured = True
                elif not manualIpAdressConfigured:
                    self.manualRouter.set(value)
            elif contains_value(line, MANUAL_NAME_SERVER_KEY):
                value = get_value(line, MANUAL_NAME_SERVER_KEY)
                if not is_commented(line):
                    self.manualNameServer.set(value)
                    manualNameServerConfigured = True
                elif not manualIpAdressConfigured:
                    self.manualNameServer.set(value)
        self.manual.set(manualIpAdressConfigured and manualRouterConfigured and manualNameServerConfigured)

    def reset(self):
        self.manual.set(False)
        self.manualIpAdress.set('')
        self.manualRouter.set('')
        self.manualNameServer.set('')

    def toLines(self, heading):
        lines = None
        if self.manual.get():
            lines = [heading,
                     MANUAL_IP_ADDRESS_KEY + "=" + self.manualIpAdress.get() + "\n",
                     MANUAL_ROUTER_KEY + "=" + self.manualRouter.get() + "\n",
                     MANUAL_NAME_SERVER_KEY + "=" + self.manualNameServer.get() + "\n", "\n"]
        else:
            lines = ["#" + heading,
                     "#" + MANUAL_IP_ADDRESS_KEY + "=" + self.manualIpAdress.get() + "\n",
                     "#" + MANUAL_ROUTER_KEY + "=" + self.manualRouter.get() + "\n",
                     "#" + MANUAL_NAME_SERVER_KEY + "=" + self.manualNameServer.get() + "\n", "\n"]
        return lines
