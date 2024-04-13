from tkinter import StringVar, BooleanVar
import json
import os


CURRENT_GUI_FOLDER = os.path.dirname(os.path.realpath(__file__))
GUI_SUPER_FOLDER = '/home/pi'
GUI_STATICS_FOLDER = GUI_SUPER_FOLDER + '/rf-kit-statics'
GUI_PATH_JSON_FILE = GUI_STATICS_FOLDER + '/gui_path.json'

CONFIG_FILE = GUI_STATICS_FOLDER + "/config.json"
FTP_CONFIG_KEY = "ftp"
CUSTOM_DEVICE_NAME_KEY = "customDeviceName"
OPERATIONAL_INTERFACE_KEY = "operational_interface"
CAT_CONFIG_KEY = "cat_config"
CURSOR_KEY = "cursor"
LOW_POWER_KEY = "is_low_power"
UDP_CONFIG_KEY = "udp_config"
SELECTED_ANTENNAS_KEY = "selected_antennas"
SLEEP_TIMER_KEY = "sleep_timer"
DISPLAY_STATUS_KEY = "display_on"
SCALE_TYPE_KEY = "scale_type"
RASPI_BOOT_CONFIG_VERSION_KEY = "raspi_boot_config_version"
TCI_CONFIG_KEY = "tci_config"
CAN_POWER_KEY = "can_power"
CUSTOM_ANTENNA_NAMES_KEY = "custom_antenna_names"




class Config:
    instance = None

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            #load config
            cls.instance = Config()
        return cls.instance

    def __init__(self):
        self.ftpConfig = self.load(FTP_CONFIG_KEY)
        self.savedCustomDeviceName = self.load(CUSTOM_DEVICE_NAME_KEY)
        self.customDeviceNameVar = StringVar(value=self.savedCustomDeviceName)
        self.operationalInterfaceVar = StringVar(value=self.load_with_default(OPERATIONAL_INTERFACE_KEY, 'UNIVERSAL'))
        self.catConfig = self.load_with_default(CAT_CONFIG_KEY, {"manufacturer": None, "rig": None, "baud_rate": None})
        self.cursorVar = StringVar(value=self.load_with_default(CURSOR_KEY, 'none'))
        self.isLowPower = BooleanVar(value=self.load_with_default(LOW_POWER_KEY, True))
        self.udpConfig = self.load_with_default(UDP_CONFIG_KEY, {"port": 12060})
        self.savedSelectedAntennasPerBand = self.load_with_default(SELECTED_ANTENNAS_KEY, list(list(True for _ in range(0, 4)) for _ in range(0, 11)))
        self.selectedAntennasPerBand = two_dim_booleans_to_boolean_vars(self.savedSelectedAntennasPerBand)
        self.sleepTimerConfig = self.load_with_default(SLEEP_TIMER_KEY, {"enabled": False, "minutes": 20})
        self.displayOn = BooleanVar(value=self.load_with_default(DISPLAY_STATUS_KEY, True))
        self.scaleTypeVar = StringVar(value=self.load_with_default(SCALE_TYPE_KEY, "Standard"))
        self.raspiBootConfigVersion = self.load_with_default(RASPI_BOOT_CONFIG_VERSION_KEY, 1)
        self.tciConfig = self.load_with_default(TCI_CONFIG_KEY, {"port": 40001})
        self.canPower = self.load_with_default(CAN_POWER_KEY, {"voltage": 53.5})
        self.savedCustomAntennaNames = self.load_with_default(CUSTOM_ANTENNA_NAMES_KEY, ['ANT 1', 'ANT 2', 'ANT 3', 'ANT 4'])
        self.customAntennaNameVars = one_dim_strings_to_string_vars(self.savedCustomAntennaNames)

    def saveCustomDeviceName(self):
        custom_device_name_to_save = self.customDeviceNameVar.get()
        self.save(CUSTOM_DEVICE_NAME_KEY, custom_device_name_to_save)
        self.savedCustomDeviceName = custom_device_name_to_save

    def saveOperationalInterface(self):
        self.save(OPERATIONAL_INTERFACE_KEY, self.operationalInterfaceVar.get())

    def save_cat_config(self):
        self.save(CAT_CONFIG_KEY, self.catConfig)

    def save_cursor(self):
        self.save(CURSOR_KEY, self.cursorVar.get())

    def save_high_low_power(self):
        self.save(LOW_POWER_KEY, self.isLowPower.get())

    def save_udp_config(self):
        self.save(UDP_CONFIG_KEY, self.udpConfig)

    def save_selected_antennas(self):
        selected_antennas_per_band_to_save = two_dim_boolean_vars_to_booleans(self.selectedAntennasPerBand)
        self.save(SELECTED_ANTENNAS_KEY, selected_antennas_per_band_to_save)
        self.savedSelectedAntennasPerBand = selected_antennas_per_band_to_save

    def save_sleep_timer_config(self):
        self.save(SLEEP_TIMER_KEY, self.sleepTimerConfig)

    def save_display_status(self):
        self.save(DISPLAY_STATUS_KEY, self.displayOn.get())

    def save_scale_type(self):
        self.save(SCALE_TYPE_KEY, self.scaleTypeVar.get())

    def save_raspi_boot_config_version(self):
        self.save(RASPI_BOOT_CONFIG_VERSION_KEY, self.raspiBootConfigVersion)

    def save_tci_config(self):
        self.save(TCI_CONFIG_KEY, self.tciConfig)

    def save_can_power(self):
        self.save(CAN_POWER_KEY, self.canPower)

    def save_custom_antenna_names(self):
        custom_names_to_save = one_dim_string_vars_to_strings(self.customAntennaNameVars)
        self.save(CUSTOM_ANTENNA_NAMES_KEY, custom_names_to_save)
        self.savedCustomAntennaNames = custom_names_to_save

    def load(self, key):
        config_json_data = self.load_config_json_from_file()
        return config_json_data[key]

    def load_with_default(self, key, default_value):
        config_json_data = self.load_config_json_from_file()
        value = config_json_data.get(key)
        if value is None:
            self.save(key, default_value)
            return default_value
        else:
            return value

    def save(self, key, value):
        config_json_data = self.load_config_json_from_file()
        config_json_data[key] = value
        self.write_config_json_to_file(config_json_data)

    def load_config_json_from_file(self):
        with open(CONFIG_FILE) as config_file:
            config_json_data = json.load(config_file)
        return config_json_data

    def write_config_json_to_file(self, config_json_data):
        with open(CONFIG_FILE, "w") as config_file:
            json.dump(config_json_data, config_file, indent=2)
        os.system('sync')

    def ensure_consistency_with(self, default_antennas):
        for index, default in enumerate(default_antennas):
            self.selectedAntennasPerBand[index][default].set(True)


def two_dim_booleans_to_boolean_vars(two_dim_booleans):
    return list(one_dim_booleans_to_boolean_vars(booleans) for booleans in two_dim_booleans)


def one_dim_booleans_to_boolean_vars(booleans):
    return list(BooleanVar(value=boolean) for boolean in booleans)


def one_dim_strings_to_string_vars(strings):
    return list(StringVar(value=string) for string in strings)


def two_dim_boolean_vars_to_booleans(two_dim_boolean_vars):
    return list(one_dim_boolean_vars_to_booleans(boolean_vars) for boolean_vars in two_dim_boolean_vars)


def one_dim_boolean_vars_to_booleans(boolean_vars):
    return list(boolean_var.get() for boolean_var in boolean_vars)

def one_dim_string_vars_to_strings(string_vars):
    return list(string_var.get() for string_var in string_vars)
