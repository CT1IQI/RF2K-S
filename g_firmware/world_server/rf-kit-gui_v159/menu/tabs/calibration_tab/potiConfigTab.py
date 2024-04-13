from tkinter import *
from tkinter import ttk

from data import Data


class PotiConfigTab(ttk.Frame):

    def __init__(self, delegate, container):
        super().__init__(container)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.delegate = delegate

        self.container = ttk.Frame(self, pad=30)
        self.container.grid_propagate(False)
        self.container.grid(row=0, column=0, sticky="wnes")

        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.createPotis()
        self.createCloseButton()

    def createPotis(self):
        potiContainer = ttk.Frame(self.container)
        for row in range(3):
            potiContainer.rowconfigure(row, weight=1, uniform="fred")

        for column in range(3):
            potiContainer.columnconfigure(column, weight=1, uniform="fred")
        potiContainer.grid(row=0, column=0, sticky="wnes")

        labels = ["", "", "PF", "PAF", "PR"]
        labelVars = [Data.getInstance().vars.voltage,
                     Data.getInstance().vars.current,
                     Data.getInstance().vars.P_dF,
                     Data.getInstance().vars.P_dAF,
                     Data.getInstance().vars.P_dR]
        for i in range(5):
            container = ttk.Frame(potiContainer, style="Poti.TFrame")
            container.rowconfigure(0, weight=1)
            container.columnconfigure(0, weight=1)
            container.grid(row=(i // 3), column=(i % 3), padx=20, pady=20, sticky="wnes")
            ttk.Label(container, textvariable=labelVars[i], style="Value.Poti.TLabel").grid(row=0, column=0)
            ttk.Label(container, text=labels[i], style="Label.Poti.TLabel").grid(row=0, column=0, padx=(0, 5), pady=(0, 5), sticky="se")

    def createCloseButton(self):
        ttk.Button(self.container, text="Close", pad=(40, 20), style="Settings.TButton", command=self.onCloseClicked)\
            .grid(row=1, column=0, sticky="se")

    def onCloseClicked(self):
        self.delegate.onCloseClicked()
