import os

from config import Config

CURRENT_RASPI_BOOT_CONFIG_VERSION = 2
CURRENT_RASPI_BOOT_CONFIG_FILE = "resources/config_v2.txt"
RASPI_BOOT_CONFIG_PATH = "/boot/config.txt"


def update_boot_config_if_outdated():
    if Config.get_instance().raspiBootConfigVersion < CURRENT_RASPI_BOOT_CONFIG_VERSION:
        copy_command = "cp " + CURRENT_RASPI_BOOT_CONFIG_FILE + " " + RASPI_BOOT_CONFIG_PATH
        sync_command = "sync " + RASPI_BOOT_CONFIG_PATH
        command = copy_command + " && " + sync_command
        os.system("sudo bash -c \"" + command + "\"")
        Config.get_instance().raspiBootConfigVersion = CURRENT_RASPI_BOOT_CONFIG_VERSION
        Config.get_instance().save_raspi_boot_config_version()
        return True
    else:
        return False
