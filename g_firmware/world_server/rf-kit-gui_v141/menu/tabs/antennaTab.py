from tkinter import ttk, IntVar

from interface import InterfaceWrapper
from config import Config
from data import Data, BANDS
from keyboard.keyboard import Keyboard
from menu import window_elements


class AntennaSelection(ttk.Frame):

    def __init__(self, container, bands, defaultAntennas):
        super().__init__(container)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.bands = bands
        self.defaultAntennas = list([IntVar(value=default) for default in defaultAntennas])
        self.antennas_per_column = int(len(self.bands) / 2 + 0.5)

        self.table_frame = ttk.Frame(self)
        self.table_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=(0, 10))
        for i in range(self.antennas_per_column):
            self.table_frame.rowconfigure(i + 3, weight=1)
        self.number_of_antennas = 4
        for i in range(self.number_of_antennas * 2 + 2):
            if i % (self.number_of_antennas + 1) == 0:
                self.table_frame.columnconfigure(i, weight=1, uniform="band")
            else:
                self.table_frame.columnconfigure(i, weight=1, uniform="antenna")

        self.createHeader()
        self.createBands()

    def createHeader(self):
        ttk.Label(self.table_frame, text="Band").grid(row=0, column=0)
        ttk.Label(self.table_frame, text="Available Antennas").grid(row=0, column=1, columnspan=self.number_of_antennas)
        ttk.Label(self.table_frame, text="Band").grid(row=0, column=1+self.number_of_antennas)
        ttk.Label(self.table_frame, text="Available Antennas")\
            .grid(row=0, column=2+self.number_of_antennas, columnspan=self.number_of_antennas)
        ttk.Frame(self.table_frame, height=2, style="Separator.TFrame")\
            .grid(row=1, column=0, columnspan=2+self.number_of_antennas*2, pady=10, sticky="we")
        for i, antennaVar in enumerate(Config.get_instance().customAntennaNameVars):
            antenna_name_entry = ttk.Entry(self.table_frame, textvariable=antennaVar, style="Antenna.Config.TEntry", width=10)
            antenna_name_entry.grid(row=2, column=(i + 1))
            antenna_name_entry.bind("<ButtonRelease-1>", lambda e, var=antennaVar: Keyboard(self, var, lambda: self.on_keyboard_ok))
            antennaVar.trace("w", lambda *args, var=antennaVar: self.limit_antenna_name_length(var))
            ttk.Label(self.table_frame, textvariable=antennaVar, style="Antenna.TLabel").grid(row=2, column=(i + 2 + self.number_of_antennas))

    def on_keyboard_ok(self):
        pass

    def limit_antenna_name_length(self, antenna_var):
        text = antenna_var.get()
        if len(text) > 5:
            antenna_var.set(text[:5])


    def createBands(self):
        for i, band in enumerate(self.bands[::-1]):
            if i < self.antennas_per_column:
                row_offset = 3
                column_offset = 0
            else:
                row_offset = 3 - self.antennas_per_column
                column_offset = 1 + self.number_of_antennas
            row = (i + row_offset)

            band_idx = len(self.bands) - i - 1
            ttk.Label(self.table_frame, text=band).grid(row=row, column=column_offset)
            checkboxes = []
            for j in range(0, self.number_of_antennas):
                checkbox = ttk.Checkbutton(self.table_frame, style="Antenna.Radiobuttonlike.TCheckbutton",
                                           variable=Config.get_instance().selectedAntennasPerBand[band_idx][j])
                checkbox.grid(row=row, column=(column_offset+j+1))
                checkboxes.append(checkbox)
                checkbox.configure(command=lambda bound_checkboxes=checkboxes:
                                   self.set_checkboxes_state(bound_checkboxes))
            self.set_checkboxes_state(checkboxes)

    def set_checkboxes_state(self, checkboxes):
        selected_checkboxes = []
        for checkbox in checkboxes:
            if checkbox.instate(['selected']):
                selected_checkboxes.append(checkbox)
        if len(selected_checkboxes) > 1:
            new_state = '!disabled'
        else:
            new_state = 'disabled'
        for checkbox in selected_checkboxes:
            checkbox.configure(state=new_state)


class Antennas(ttk.Frame):

    def __init__(self, delegate, container):
        super().__init__(container, pad=30)
        self.grid_propagate(False)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1, uniform="fred")
        self.grid(row=0, column=0, sticky="wnes")

        self.delegate = delegate

        self.use_ext_antenna = IntVar(value=Data.getInstance().vars.useExtAntenna.get())  # cannot use Data variable here directly because it is updated all the time
        self.ext_antenna_high_low_active = IntVar(value=Data.getInstance().externalAntennaHighLowActive)

        self.createBands()
        self.create_bottom_container()

    def createBands(self):
        antennaSelection = AntennaSelection(self, BANDS, Data.getInstance().defaultAntennas)
        antennaSelection.grid(row=0, column=0, sticky="wnes")

    def create_bottom_container(self):
        bottom_container = ttk.Frame(self)
        bottom_container.rowconfigure(0, weight=1)
        bottom_container.columnconfigure(3, weight=1)
        bottom_container.grid(row=1, column=0, sticky="we")
        self.create_ext_antenna(bottom_container)
        self.createSaveButton(bottom_container)
        self.createCloseButton(bottom_container)

    def create_ext_antenna(self, container):
        frame = ttk.Frame(container)
        frame.grid(row=0, column=0, sticky="nwes")
        frame.rowconfigure(1, weight=1)

        ttk.Frame(frame, height=2, style="Separator.TFrame") \
            .grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="nwe")

        window_elements.create_check_button_with_text(frame, "Ext. Antenna switch", style='Small.TCheckbutton',
                                                      variable=self.use_ext_antenna, onvalue=1, offvalue=0)\
            .grid(row=1, column=0)

        window_elements.create_radio_button_with_text(frame, "active high", variable=self.ext_antenna_high_low_active,
                                                      value=1, style='Small.TRadiobutton').grid(row=1, column=1, padx=5)
        window_elements.create_radio_button_with_text(frame, "active low", variable=self.ext_antenna_high_low_active,
                                                      value=0, style='Small.TRadiobutton').grid(row=1, column=2, padx=5)

    def createSaveButton(self, container):
        window_elements.create_responding_menu_button(container, "Save", self.onSaveClicked) \
            .grid(row=0, column=3, sticky="se")

    def createCloseButton(self, container):
        ttk.Button(container, text="Close", pad=(40, 20), style="Settings.TButton", command=self.onCloseClicked) \
            .grid(row=0, column=4, sticky="se")

    def onSaveClicked(self):
        for band_index, default_antenna in enumerate(Data.getInstance().defaultAntennas):
            default_antenna_selected = Config.get_instance().selectedAntennasPerBand[band_index][default_antenna].get()
            if not default_antenna_selected:
                for antenna, is_selected_var in enumerate(Config.get_instance().selectedAntennasPerBand[band_index]):
                    if is_selected_var.get():
                        InterfaceWrapper.getInstance().set_default_antenna(band_index, antenna)
                        Data.getInstance().defaultAntennas[band_index] = antenna
                        break
        InterfaceWrapper.getInstance().set_use_ext_antenna(self.use_ext_antenna.get())
        new_high_low = self.ext_antenna_high_low_active.get()
        InterfaceWrapper.getInstance().set_ext_antenna_high_low_active(new_high_low)
        # update value in Data because it is not updated in getAllVars()
        Data.getInstance().externalAntennaHighLowActive = new_high_low
        Config.get_instance().save_custom_antenna_names()
        Config.get_instance().save_selected_antennas()

    def onCloseClicked(self):
        self.delegate.onCloseClicked()
