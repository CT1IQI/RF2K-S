from tkinter import *
from tkinter import ttk
from tkinter import messagebox

import re
import os

from data import Data
import update


class UpdateTab(ttk.Frame):

    def __init__(self, delegate, container):
        super().__init__(container)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.delegate = delegate

        self.availableVersions = (0, 0)

        self.container = ttk.Frame(self, pad=30)
        self.container.grid_propagate(False)
        self.container.grid(row=0, column=0, sticky="wnes")

        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)
        self.createCloseButton()

        self.checkForUpdatesContainer = None
        self.updateContainer = None
        self.checkingContainer = None
        self.contentContainers = []

        self.installedVersionVar = StringVar()
        self.availableVersionVar = StringVar()
        self.installedGuiVersionVar = StringVar()
        self.availableGuiVersionVar = StringVar()

        self.displayCheckForUpdatesButton()

    def hideAllContentContainersExcept(self, notToHide):
        [container.grid_remove() for container in self.contentContainers if container is not notToHide]

    def displayCheckForUpdatesButton(self):
        self.hideAllContentContainersExcept(self.checkForUpdatesContainer)
        if self.checkForUpdatesContainer is not None:
            self.checkForUpdatesContainer.grid()
            return
        self.checkForUpdatesContainer = ttk.Frame(self.container)
        self.contentContainers.append(self.checkForUpdatesContainer)
        self.checkForUpdatesContainer.rowconfigure(0, weight=1)
        self.checkForUpdatesContainer.columnconfigure(0, weight=1)
        self.checkForUpdatesContainer.grid(row=0, column=0, sticky="wnes")
        ttk.Button(self.checkForUpdatesContainer, text="Check For Updates", pad=(40, 20), style="Settings.TButton", command=self.onCheckForUpdatesClicked).grid(row=0, column=0)

    def createVersionContainer(self, container, row, column, versionType, installedVersionVar, availableVersionVar):
        container = ttk.Frame(container)
        container.grid(row=row, column=column)
        ttk.Label(container, text=versionType, anchor="center", style="VersionType.Update.TLabel").grid(row=0, column=0, pady=(0, 20), sticky="wnes")
        ttk.Label(container, textvariable=installedVersionVar, anchor="center").grid(row=1, column=0, sticky="wnes")
        ttk.Label(container, textvariable=availableVersionVar, anchor="center").grid(row=2, column=0, sticky="wnes")

    def displayVersionsAndUpdateButton(self):
        self.hideAllContentContainersExcept(self.updateContainer)
        self.installedVersionVar.set("Installed Version: {:s}".format(str(Data.getInstance().version)))
        self.availableVersionVar.set("Available Version: {:s}".format(str(self.availableVersions[1])))
        self.installedGuiVersionVar.set("Installed Version: {:s}".format(str(Data.getInstance().guiVersion)))
        self.availableGuiVersionVar.set("Available Version: {:s}".format(str(self.availableVersions[0])))
        if self.updateContainer is not None:
            self.updateContainer.grid()
        else:
            self.updateContainer = ttk.Frame(self.container)
            self.contentContainers.append(self.updateContainer)
            for row in range(2):
                self.updateContainer.rowconfigure(row, weight=1, uniform="fred")
            for column in range(2):
                self.updateContainer.columnconfigure(column, weight=1, uniform="fred")
            self.updateContainer.grid(row=0, column=0, sticky="wnes")
            self.createVersionContainer(self.updateContainer, 0, 0, "GUI", self.installedGuiVersionVar, self.availableGuiVersionVar)
            self.createVersionContainer(self.updateContainer, 0, 1, "Controller", self.installedVersionVar, self.availableVersionVar)
            self.updateButton = ttk.Button(self.updateContainer, text="Update", pad=(40, 20), style="Settings.TButton", command=self.onUpdateClicked)
            self.updateButton.grid(row=1, column=0, columnspan=2)
        if Data.getInstance().guiVersion >= self.availableVersions[0] and Data.getInstance().version >= self.availableVersions[1]:
            self.updateButton.state([("disabled")])

    def createCloseButton(self):
        ttk.Button(self.container, text="Close", pad=(40, 20), style="Settings.TButton", command=self.onCloseClicked) \
            .grid(row=1, column=0, sticky="se")

    def onCloseClicked(self):
        self.delegate.onCloseClicked()

    def onCheckForUpdatesClicked(self):
        self.hideAllContentContainersExcept(self.updateContainer)
        if self.checkingContainer is not None:
            self.checkingContainer.grid()
        else:
            self.checkingContainer = ttk.Frame(self.container)
            self.contentContainers.append(self.checkingContainer)
            self.checkingContainer.grid(row=0, column=0)
            ttk.Label(self.checkingContainer, text="Checking for updates...").grid(row=0, column=0)
        self.after(1000, self.startUpdatesCheck)

    def startUpdatesCheck(self):
        try:
            self.availableVersions = update.get_available_versions()
        except Exception as e:
            retry = messagebox.showerror(parent=self, title="Update check failed", message="An error occurred while checking for updates.", type="retrycancel")
            if retry == "retry":
                self.startUpdatesCheck()
            else:
                self.displayCheckForUpdatesButton()
            return

        self.displayVersionsAndUpdateButton()

    def onUpdateClicked(self):
        self.delegate.onUpdateClicked(self)

    def onUpdateFailed(self):
        retry = messagebox.showerror(parent=self, title="Update failed", message="The update process failed. Try again.", type="retrycancel")
        if not retry:
            return

    def onUpdateFinished(self):
        pass
