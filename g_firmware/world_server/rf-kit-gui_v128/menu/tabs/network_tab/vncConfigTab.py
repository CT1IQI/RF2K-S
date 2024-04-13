from tkinter import ttk, BooleanVar

from menu import window_elements
from network.vncConfig import VncConfig, MIN_VNC_PASSWORD_LENGTH


class VncConfigTab(ttk.Frame):
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

        self.passwordLabel = None
        self.passwordEntry = None
        self.noPasswordLabelContainer = None
        self.noPasswordEntryContainer = None

        self.saveButton = None

        self.createConfigContainer()

        self.createBottomContainer()

    def createConfigContainer(self):
        config_container = ttk.Frame(self.container)
        config_container.grid(row=1, column=0, sticky="wnes")
        config_container.rowconfigure(3, weight=1)
        config_container.columnconfigure(0, weight=1)
        config_container.columnconfigure(3, weight=1)

        ttk.Label(config_container, text="Port").grid(row=0, column=1, padx=20, sticky='E')
        spinbox_container = window_elements.create_custom_spinbox_container(config_container, VncConfig.get_instance().port)
        spinbox_container.grid(row=0, column=2, pady=5)


        ttk.Label(config_container, text="Change Password").grid(row=1, column=1, padx=10, pady=10, sticky='E')
        ttk.Checkbutton(config_container, variable=VncConfig.get_instance().changePassword,
                        command=self.show_or_remove_password, takefocus=False).grid(row=1, column=2, padx=10, pady=10)

        self.passwordLabel = ttk.Label(config_container, text="New Password (>= 6 characters)")
        self.passwordLabel.grid(row=2, column=1, padx=10, pady=10, sticky='E')
        self.passwordEntry, self.passwordErrorMessage = window_elements.create_secret_entry(config_container, VncConfig.get_instance().newPassword,
                                                                 self.password_long_enough, "password must have at least 6 characters")
        self.passwordEntry.grid(row=2, column=2, padx=10, pady=(10, 0), sticky="we")
        self.passwordErrorMessage.grid(row=2, column=3)
        self.noPasswordLabelContainer = ttk.Frame(config_container)
        self.noPasswordLabelContainer.grid(row=2, column=1, sticky="wnes")
        self.noPasswordEntryContainer = ttk.Frame(config_container)
        self.noPasswordEntryContainer.grid(row=2, column=2, sticky="wnes")
        self.noPasswordErrorContainer = ttk.Frame(config_container)
        self.noPasswordErrorContainer.grid(row=2, column=3, sticky="wnes")

        self.show_or_remove_password()

    def password_long_enough(self):
        is_valid = len(VncConfig.get_instance().newPassword.get()) >= MIN_VNC_PASSWORD_LENGTH
        self.update_save_button_state(is_valid)
        return is_valid


    def show_or_remove_password(self):
        if VncConfig.get_instance().changePassword.get():
            self.passwordLabel.lift(self.noPasswordLabelContainer)
            self.passwordEntry.lift(self.noPasswordEntryContainer)
            self.passwordErrorMessage.lift(self.noPasswordErrorContainer)
        else:
            self.passwordLabel.lower(self.noPasswordLabelContainer)
            self.passwordEntry.lower(self.noPasswordEntryContainer)
            self.passwordErrorMessage.lower(self.noPasswordErrorContainer)
        self.update_save_button_state()

    def createBottomContainer(self):
        bottom_container = ttk.Frame(self.container)
        bottom_container.grid_propagate(True)
        bottom_container.grid(row=2, column=0, sticky="wnes")
        bottom_container.rowconfigure(0, weight=1)
        bottom_container.columnconfigure(0, weight=1)

        self.saveButton = window_elements\
            .create_responding_menu_button(bottom_container, "Save and apply", self.on_save_and_apply_clicked)
        self.saveButton.grid(row=1, column=1, sticky="se")
        ttk.Button(bottom_container, text="Close", pad=(40, 20), style="Settings.TButton", command=self.onCloseClicked)\
            .grid(row=1, column=2, sticky="se")
        self.update_save_button_state()

    def update_save_button_state(self, password_valid = None):
        if self.saveButton is None:
            return
        if (not VncConfig.get_instance().changePassword.get()) or self.booleanIfNotNoneElsePasswordEntryValid(password_valid):
            self.saveButton["state"] = "normal"
        else:
            self.saveButton["state"] = "disabled"

    def booleanIfNotNoneElsePasswordEntryValid(self, boolean):
        if boolean is not None:
            return boolean
        else:
            return self.passwordEntry.instate(["!invalid"])

    def on_save_and_apply_clicked(self):
        VncConfig.get_instance().save_and_apply()

    def onCloseClicked(self):
        self.delegate.onCloseClicked()
