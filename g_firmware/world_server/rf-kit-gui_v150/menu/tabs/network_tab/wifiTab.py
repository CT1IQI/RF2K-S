import os
from tkinter import ttk, messagebox, SUNKEN

from keyboard.secretKeyboard import SecretKeyboard
from menu import window_elements
from menu.tabs.network_tab.abstractNetworkTab import AbstractNetworkTab
from network.networkConfig import NetworkConfig
from network.wpaConfig import WpaConfig

WIFI_INTERFACE = "wlan0"


class WifiTab(AbstractNetworkTab):
    def __init__(self, delegate, container):
        self.wifiCombobox = None
        self.passwordEntry = None
        super(WifiTab, self).__init__(delegate, container)

    def getDhcpConfig(self):
        return NetworkConfig.get_instance().wlanDhcp

    def on_save_and_apply_clicked(self):
        NetworkConfig.get_instance().save_WLAN()
        WpaConfig.get_instance().save_and_apply_WPA()

    def restore_default(self):
        NetworkConfig.get_instance().reset_WLAN()
        WpaConfig.get_instance().reset_and_apply_WPA()

    def get_interface_name(self):
        return WIFI_INTERFACE

    def createSpecificConfig(self, specific_config_container):
        ttk.Button(specific_config_container, text="Scan", pad=(40, 20), style="Settings.TButton",
                   command=self.on_scan_clicked).grid(row=0, column=0, pady=10)

        self.wifiCombobox = ttk.Combobox(specific_config_container, textvariable=WpaConfig.get_instance().newWlanName, values=[],
                                         state="disabled", height=4)
        self.wifiCombobox.grid(row=1, column=0, padx=10, pady=10, sticky="we")
        self.wifiCombobox.bind("<<ComboboxSelected>>", self.on_wlan_selected)

        password_container = ttk.Frame(specific_config_container)
        password_container.grid(row=2, column=0, sticky="we")
        password_container.columnconfigure(1, weight=1)
        ttk.Label(password_container, text="Password").grid(row=0, column=0, padx=10, pady=10)
        password_entry, validation_error_label = window_elements.create_secret_entry(password_container,
                                                                                     WpaConfig.get_instance()
                                                                                     .newWlanPassword,
                                                                                     self.validate_passphrase,
                                                                                     "password must have between 8 and 63 characters")
        password_entry.grid(row=0, column=1, padx=10, pady=10, sticky="we")
        validation_error_label.grid(row=1, column = 1, padx=10)

        #self.passwordEntry = ttk.Entry(password_container, textvariable=WpaConfig.get_instance().newWlanPassword, show="*", style='Config.TEntry',
        #                     font=("Lato", 18), validatecommand=self.validate_passphrase)
        #self.passwordEntry.grid(row=0, column=1, padx=10, pady=10, sticky="we")
        #self.passwordEntry.bind("<ButtonRelease-1>", lambda e: SecretKeyboard(self, WpaConfig.get_instance().newWlanPassword,
        #                                                     lambda: self.on_password_entered))


    def validate_passphrase(self):
        return WpaConfig.get_instance().is_password_valid()

    def on_scan_clicked(self):
        try:
            wlan_names = [line.split('"')[1] for line
                          in os.popen('iwlist ' + WIFI_INTERFACE + ' scan | grep ESSID').read().splitlines()]
            self.wifiCombobox.configure(values=list(wlan_names), state="readonly")
        except Exception as e:
            retry = messagebox.showerror(parent=self, title="WLAN scan failed",
                                         message="An error occurred while scanning WLAN networks.", type="retrycancel")
            if retry == "retry":
                self.on_scan_clicked()
            return

    def on_wlan_selected(self, event):
        WpaConfig.get_instance().newWlanPassword.set("")

