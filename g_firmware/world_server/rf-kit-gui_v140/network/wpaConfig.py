import os
from tkinter import StringVar

WPA_SUPPLICANT_PATH = "/etc/wpa_supplicant/wpa_supplicant.conf"

STATIC_WPA_PART = """ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=GB
"""

class WpaConfig:
    instance = None

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            # load config
            cls.instance = WpaConfig()
        return cls.instance

    def __init__(self):
        self.newWlanName = StringVar()
        self.newWlanPassword = StringVar()

    def is_password_valid(self):
        pw_length = len(self.newWlanPassword.get())
        return 8 <= pw_length <= 63

    # WLAN DHCP config must be saved first
    def save_and_apply_WPA(self):
        pw_length = len(self.newWlanPassword.get())
        if not self.is_password_valid():
            print('ERROR: password length < 8 or > 63')
            return
        os.system(
            "sudo bash -c \"wpa_passphrase '" + self.newWlanName.get() + "' '" + self.newWlanPassword.get() +
            "' | grep -v '#psk' >> " + WPA_SUPPLICANT_PATH + "\"")
        self.sync_and_reconfigure()

    def reset_and_apply_WPA(self):
        os.system(
            "sudo bash -c \"echo '" + STATIC_WPA_PART + "' > " + WPA_SUPPLICANT_PATH + "\"")
        self.newWlanName.set('')
        self.newWlanPassword.set('')
        self.sync_and_reconfigure()

    def sync_and_reconfigure(self):
        os.system('sync')
        ret_val = os.system('sudo wpa_cli -i wlan0 reconfigure')
        if ret_val != 0:
            print("error reconfiguring wlan0")
