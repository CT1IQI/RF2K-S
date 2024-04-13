from enum import Enum
from tkinter import *
from tkinter import ttk

from interface import InterfaceWrapper
from debug.debugCalibrationEnums import Band, DebugCalibrationType
from menu import window_elements
from menu.tabs.debug_tab.calibration_summary_tab.debugCalibrationTab import DebugCalibrationTab




class InputCalibrationTab(DebugCalibrationTab):

    def __init__(self, delegate, container):
        super().__init__(delegate, container, DebugCalibrationType.INPUT)
        self.offsetView = BooleanVar(value=True)
        self.offsetView.trace_add("write", lambda *args: self.update_all_digits())

        self.create_view_switch()
        self.create_save_button()

    def create_view_switch(self):
        window_elements.create_radio_button_with_text(self.bottom_container, "show absolute values", variable=self.offsetView,
                                                      value=0, style='Small.TRadiobutton').grid(row=1, column=0, padx=5)
        window_elements.create_radio_button_with_text(self.bottom_container, "show offsets", variable=self.offsetView,
                                                      value=1, style='Small.TRadiobutton').grid(row=1, column=1, padx=5)

    def create_save_button(self):
        window_elements.create_responding_menu_button(self.bottom_container, "Save offsets", self.on_save_clicked) \
            .grid(row=1, column=2, sticky="se")

    def update_digit(self, filter_key: Band, digits_var: IntVar = None):
        if digits_var is None:
            digits_var = self.digitsVarsByFilter[filter_key]
        current_digits = InterfaceWrapper.getInstance().get_dac_offset(DebugCalibrationType.INPUT_OFFSET if self.offsetView.get() else DebugCalibrationType.INPUT, filter_key)
        digits_var.set(current_digits)


    def on_save_clicked(self):
        InterfaceWrapper.getInstance().save_dac_value_input_offsets()
