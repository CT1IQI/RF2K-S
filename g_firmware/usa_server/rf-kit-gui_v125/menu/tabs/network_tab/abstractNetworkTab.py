from abc import ABC, abstractmethod
from tkinter import ttk, StringVar

import networking
from keyboard.keyboard import Keyboard
from menu import window_elements


class AbstractNetworkTab(ABC, ttk.Frame):
    def __init__(self, delegate, container):
        super().__init__(container)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.delegate = delegate

        self.container = ttk.Frame(self, pad=30)
        self.container.grid_propagate(False)
        self.container.grid(row=0, column=0, sticky="wnes")
        self.container.rowconfigure(1, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.currentIpVar = StringVar()
        self.createStatusContainer()

        self.dhcp_container = None
        self.manual_container = None
        self.createConfigContainer()

        self.createBottomContainer()

    def createStatusContainer(self):
        status_container = ttk.Frame(self.container)
        status_container.rowconfigure(0, weight=1)
        status_container.columnconfigure(1, weight=1)
        status_container.grid(row=0, column=0, sticky="wnes", pady=(0,20))
        ttk.Label(status_container, text="IP Address").grid(row=0, column=0)
        ttk.Label(status_container, textvariable=self.currentIpVar, style="IP.TLabel").grid(row=0, column=1, padx=(10, 0), sticky="we")
        self.update_current_ip()

    def createConfigContainer(self):
        config_container = ttk.Frame(self.container)
        config_container.grid(row=1, column=0, sticky="wnes")
        config_container.rowconfigure(0, weight=1)
        config_container.columnconfigure(0, weight=1)
        config_container.columnconfigure(1, weight=1)
        network_config_container = ttk.Frame(config_container)
        network_config_container.grid(row=0, column=0, sticky="wnes")
        specific_config_container = ttk.Frame(config_container)
        specific_config_container.grid(row=0, column=1, sticky="wnes")
        self.createNetworkConfig(network_config_container)
        self.createSpecificConfig(specific_config_container)

    def createNetworkConfig(self, network_config_container):
        modus_container = ttk.Frame(network_config_container)
        modus_container.grid(row=0, column=0, sticky="we", pady=10)
        modus_container.columnconfigure(0, weight=1)
        modus_container.columnconfigure(1, weight=1)
        window_elements.create_radio_button_with_text(modus_container, text="DHCP", variable=self.getDhcpConfig().manual,
                        command=self.on_network_mode_changed, value=False).grid(row=0, column=0)
        window_elements.create_radio_button_with_text(modus_container, text="Manual", variable=self.getDhcpConfig().manual,
                        command=self.on_network_mode_changed, value=True).grid(row=0, column=1)
        self.dhcp_container = ttk.Frame(network_config_container)
        self.dhcp_container.grid(row=1, column=0, sticky="wnes")
        self.manual_container = ttk.Frame(network_config_container)
        self.manual_container.grid(row=1, column=0, sticky="wnes")
        self.show_or_remove_manual_container()
        values_container = ttk.Frame(self.manual_container)
        values_container.grid(row=0, column=0)
        ttk.Label(values_container, text="IP Address").grid(row=0, column=0)
        ip_entry = ttk.Entry(values_container, textvariable=self.getDhcpConfig().manualIpAdress, style='Config.TEntry',
                             font=("Lato", 18))
        ip_entry.bind("<ButtonRelease-1>", lambda e: Keyboard(self, self.getDhcpConfig().manualIpAdress,
                                                              lambda: self.on_keyboard_ok))
        ip_entry.grid(row=0, column=1, padx=10, pady=10, sticky="we")
        ttk.Label(values_container, text="Router").grid(row=1, column=0)
        router_entry = ttk.Entry(values_container, textvariable=self.getDhcpConfig().manualRouter, style='Config.TEntry',
                             font=("Lato", 18))
        router_entry.bind("<ButtonRelease-1>", lambda e: Keyboard(self, self.getDhcpConfig().manualRouter,
                                                                  lambda: self.on_keyboard_ok))
        router_entry.grid(row=1, column=1, padx=10, pady=10, sticky="we")
        ttk.Label(values_container, text="Name Server").grid(row=2, column=0)
        name_server_entry = ttk.Entry(values_container, textvariable=self.getDhcpConfig().manualNameServer, style='Config.TEntry',
                             font=("Lato", 18))
        name_server_entry.bind("<ButtonRelease-1>", lambda e: Keyboard(self, self.getDhcpConfig().manualNameServer,
                                                                       lambda: self.on_keyboard_ok))
        name_server_entry.grid(row=2, column=1, padx=10, pady=10, sticky="we")

    @abstractmethod
    def getDhcpConfig(self):
        pass

    @abstractmethod
    def get_interface_name(self):
        pass

    def update_current_ip(self):
        self.currentIpVar.set(networking.get_ip(self.get_interface_name()))
        self.after(5000, self.update_current_ip)

    def createSpecificConfig(self, specific_config_container):
        pass

    def show_or_remove_manual_container(self):
        if self.getDhcpConfig().manual.get():
            self.manual_container.lift(self.dhcp_container)
        else:
            self.manual_container.lower(self.dhcp_container)

    def on_keyboard_ok(self):
        pass

    @abstractmethod
    def on_save_and_apply_clicked(self):
        pass

    def on_restore_default_clicked(self):
        self.restore_default()
        self.show_or_remove_manual_container()

    @abstractmethod
    def restore_default(self):
        pass

    def on_network_mode_changed(self):
        self.show_or_remove_manual_container()

    def createBottomContainer(self):
        bottom_container = ttk.Frame(self.container)
        bottom_container.grid_propagate(True)
        bottom_container.grid(row=2, column=0, sticky="wnes")
        bottom_container.rowconfigure(0, weight=1)
        bottom_container.columnconfigure(0, weight=1)

        window_elements\
            .create_responding_menu_button(bottom_container, "Restore default", self.on_restore_default_clicked)\
            .grid(row=1, column=1, sticky="se")
        window_elements\
            .create_responding_menu_button(bottom_container, "Save and apply", self.on_save_and_apply_clicked)\
            .grid(row=1, column=2, sticky="se")
        ttk.Button(bottom_container, text="Close", pad=(40, 20), style="Settings.TButton", command=self.onCloseClicked)\
            .grid(row=1, column=3, sticky="se")

    def onCloseClicked(self):
        self.delegate.onCloseClicked()
