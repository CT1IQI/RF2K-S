from tkinter import ttk, StringVar

from data import Data
from interface import InterfaceWrapper
from operationalInterface import OperationalInterfaceControl


class StatusBar(ttk.Frame):

    def __init__(self, container, big=False, with_not_tuned=False):
        self.withNotTuned = with_not_tuned
        super().__init__(container, style="Test.TFrame")
        self.rowconfigure(0, weight=1)
        error_frame = ttk.Frame(self)
        error_frame.grid(row=0, column=0, padx=20, sticky="wnes")
        style = "Huge.Status.TLabel" if big else "Status.TLabel"
        ttk.Label(error_frame, textvariable=InterfaceWrapper.getInstance().errorStringVar, anchor="w", style=style)\
            .grid(row=0, column=0, sticky="wnes")
        ttk.Label(error_frame, textvariable=Data.getInstance().vars.status, anchor="w", style=style)\
            .grid(row=0, column=1, sticky="wnes")
        if self.withNotTuned:
            self.notTunedStatus = StringVar()
            self.update_not_tuned_status()
            ttk.Label(error_frame, textvariable=self.notTunedStatus, anchor="w", style=style)\
                .grid(row=0, column=2, sticky="wnes")
            Data.getInstance().register_fetch_watcher(self.update_not_tuned_status)
        ttk.Label(error_frame, textvariable=OperationalInterfaceControl.operationalInterface.errorStringVar, anchor="w",
                  style="Warning." + style).grid(row=0, column=(3 if self.withNotTuned else 2), sticky="wnes")

    def update_not_tuned_status(self):
        if Data.getInstance().errorState is Data.ErrorState.NOT_TUNED:
            self.notTunedStatus.set("Not Tuned")
        else:
            self.notTunedStatus.set("")

    def destroy(self):
        if self.withNotTuned:
            Data.getInstance().unregister_fetch_watcher(self.update_not_tuned_status)
