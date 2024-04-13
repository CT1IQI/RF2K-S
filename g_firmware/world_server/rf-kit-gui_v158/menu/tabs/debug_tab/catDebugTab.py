from tkinter import *
from tkinter import ttk
from menu import window_elements
from operationalInterface import OperationalInterfaceControl
from operational_interface.catSupport import SupportedRig
from customlogging import log


class CatDebugTab(ttk.Frame):

    def __init__(self, delegate, container):
        super().__init__(container)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.delegate = delegate

        self.container = ttk.Frame(self, pad=30)
        self.container.grid_propagate(False)
        self.container.grid(row=0, column=0, sticky="wnes")

        self.container.rowconfigure(4, weight=1)
        self.container.columnconfigure(0, weight=1, uniform="fred")
        self.container.columnconfigure(1, weight=1, uniform="fred")

        log("CatDebugTab __init__")

        self.icom_ic_7610_configured = BooleanVar()
        self.icom_ic_7610_digi_sel = BooleanVar()
        self.icom_ic_7610_ipp = BooleanVar()
        self.icom_ic_7610_tx_inhibit = BooleanVar()
        self.icom_ic_7610_dpp = BooleanVar()
        self.icom_ic_7610_icpw2 = BooleanVar()
        self.update_icom_ic_7610_vars()
        self.create_icom_ic_7610_settings()

        self.createCloseButton()

    def update_icom_ic_7610_vars(self):
        log("CatDebugTab update_icom_ic_7610_vars")
        # TODO call when tab is actiated
        cat_interface_rig_data = OperationalInterfaceControl.operationalInterface.catInterface.rigData
        icom_ic_7610_configured = cat_interface_rig_data["model"] == SupportedRig.ICOM_IC7610.hamlibRigModel
        log("CatDebugTab update_icom_ic_7610_vars: icom_ic_7610_configured: " + str(icom_ic_7610_configured) + " (type " + str(type(icom_ic_7610_configured)) + ")")
        self.icom_ic_7610_configured.set(icom_ic_7610_configured)
        log("CatDebugTab update_icom_ic_7610_vars: icom_ic_7610_configured set ")
        if icom_ic_7610_configured:
            result_dict = OperationalInterfaceControl.operationalInterface.catInterface.multiple_get_ext_func(["digi_sel", "IPP", "TX_INHIBIT", "DPP", "ICPW2"])
            self.icom_ic_7610_digi_sel.set(result_dict["digi_sel"])
            self.icom_ic_7610_ipp.set(result_dict["IPP"])
            self.icom_ic_7610_tx_inhibit.set(result_dict["TX_INHIBIT"])
            self.icom_ic_7610_dpp.set(result_dict["DPP"])
            self.icom_ic_7610_icpw2.set(result_dict["ICPW2"])

    def create_icom_ic_7610_settings(self):
        log("CatDebugTab create_icom_ic_7610_settings")
        icom_ic_7610_settings_frame = ttk.Frame(self.container)
        # TODO only visible if icom_ic_7610_configured
        icom_ic_7610_settings_frame.grid(row=0, column=0, pady=5)
        window_elements.create_check_button_with_text(icom_ic_7610_settings_frame, "DIGI-SEL enable",
                                                      style='Small.TCheckbutton', variable=self.icom_ic_7610_digi_sel,
                                                      command=self.set_digi_sel).grid(row=0, column=0)
        window_elements.create_check_button_with_text(icom_ic_7610_settings_frame, "IP Plus",
                                                      style='Small.TCheckbutton', variable=self.icom_ic_7610_ipp,
                                                      command=self.set_ipp).grid(row=1, column=0)
        window_elements.create_check_button_with_text(icom_ic_7610_settings_frame, "TX Inhibit",
                                                      style='Small.TCheckbutton', variable=self.icom_ic_7610_tx_inhibit,
                                                      command=self.set_tx_inhibit).grid(row=2, column=0)
        window_elements.create_check_button_with_text(icom_ic_7610_settings_frame, "Digital Pre Distortion-SEL enable",
                                                      style='Small.TCheckbutton', variable=self.icom_ic_7610_dpp,
                                                      command=self.set_dpp).grid(row=3, column=0)
        window_elements.create_check_button_with_text(icom_ic_7610_settings_frame, "Icom PW2 enable",
                                                      style='Small.TCheckbutton', variable=self.icom_ic_7610_icpw2,
                                                      command=self.set_icpw2).grid(row=4, column=0)

    def set_digi_sel(self):
        if not self.icom_ic_7610_configured.get():
            return
        log("CatDebugTab set_digi_sel")
        OperationalInterfaceControl.operationalInterface.catInterface.set_ext_func("digi_sel", self.icom_ic_7610_digi_sel.get())
        self.icom_ic_7610_digi_sel.set(OperationalInterfaceControl.operationalInterface.catInterface.get_ext_func("digi_sel"))

    def set_ipp(self):
        if not self.icom_ic_7610_configured.get():
            return
        log("CatDebugTab set_ipp")
        OperationalInterfaceControl.operationalInterface.catInterface.set_ext_func("IPP", self.icom_ic_7610_ipp.get())
        self.icom_ic_7610_ipp.set(OperationalInterfaceControl.operationalInterface.catInterface.get_ext_func("IPP"))

    def set_tx_inhibit(self):
        if not self.icom_ic_7610_configured.get():
            return
        log("CatDebugTab set_tx_inhibit")
        OperationalInterfaceControl.operationalInterface.catInterface.set_ext_func("TX_INHIBIT", self.icom_ic_7610_tx_inhibit.get())
        self.icom_ic_7610_tx_inhibit.set(OperationalInterfaceControl.operationalInterface.catInterface.get_ext_func("TX_INHIBIT"))

    def set_dpp(self):
        if not self.icom_ic_7610_configured.get():
            return
        log("CatDebugTab set_dpp")
        OperationalInterfaceControl.operationalInterface.catInterface.set_ext_func("DPP", self.icom_ic_7610_dpp.get())
        self.icom_ic_7610_dpp.set(OperationalInterfaceControl.operationalInterface.catInterface.get_ext_func("DPP"))

    def set_icpw2(self):
        if not self.icom_ic_7610_configured.get():
            return
        log("CatDebugTab set_icpw2")
        OperationalInterfaceControl.operationalInterface.catInterface.set_ext_func("ICPW2", self.icom_ic_7610_icpw2.get())
        self.icom_ic_7610_icpw2.set(OperationalInterfaceControl.operationalInterface.catInterface.get_ext_func("ICPW2"))

    def createCloseButton(self):
        ttk.Button(self.container, text="Close", pad=(40, 20), style="Settings.TButton", command=self.onCloseClicked) \
            .grid(row=5, column=1, sticky="se")

    def onCloseClicked(self):
        self.delegate.onCloseClicked()
