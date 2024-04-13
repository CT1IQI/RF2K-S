from tkinter import ttk, LEFT, RIGHT

from keyboard.numberKeyboard import NumberKeyboard
from keyboard.secretKeyboard import SecretKeyboard


def create_custom_spinbox_container(parent_container, int_var, max_value=65535, min_value=0):
    spinbox_container = ttk.Frame(parent_container)
    port_spinbox = ttk.Spinbox(spinbox_container, from_=min_value, to=max_value, textvariable=int_var,
                               style='WithoutArrows.TSpinbox', font=("Lato", 18), width=7)
    port_spinbox.set(int_var.get())

    def ensure_in_range():
        if int_var.get() < min_value:
            int_var.set(min_value)
        elif int_var.get() > max_value:
            int_var.set(max_value)

    port_spinbox.bind("<ButtonRelease-1>", lambda e: NumberKeyboard(parent_container, int_var, ensure_in_range))
    port_spinbox.grid(row=0, column=1)

    decrement_button = ttk.Button(spinbox_container, text='-', style="WithoutArrowsSpinboxArrow.Settings.TButton")
    decrement_button.bind("<ButtonRelease-1>", lambda e: port_spinbox.event_generate("<<Decrement>>"), True)
    decrement_button.grid(row=0, column=0)
    increment_button = ttk.Button(spinbox_container, text='+', style="WithoutArrowsSpinboxArrow.Settings.TButton")
    increment_button.bind("<ButtonRelease-1>", lambda e: port_spinbox.event_generate("<<Increment>>"), True)
    increment_button.grid(row=0, column=2)

    return spinbox_container


def create_secret_entry(parent_container, string_var, validating_method=None,
                        validation_error_message=""):
    secret_entry = ttk.Entry(parent_container, textvariable=string_var, show="*", font=("Lato", 18))
    if validating_method is not None:
        error_label = ttk.Label(parent_container, text=validation_error_message, style='ValidationError.TLabel')
        secret_entry['style'] = 'Validated.Config.TEntry'
        secret_entry['validatecommand'] = validating_method
        secret_entry['validate'] = 'focus'
        validate_showing_error = lambda: show_or_hide_error(error_label, secret_entry.validate())
        validate_showing_error()
    else:
        error_label = None
        secret_entry['style'] = 'Config.TEntry'
    secret_entry.bind("<ButtonRelease-1>", lambda e: SecretKeyboard(parent_container, string_var, validate_showing_error
                                                                    , validating_method,
                                                                    validation_error_message))
    if error_label is not None:
        return secret_entry, error_label
    else:
        return secret_entry


def show_or_hide_error(error_label, is_valid):
    if is_valid:
        error_label.state(['alternate'])
    else:
        error_label.state(['!alternate'])


def create_responding_menu_button(parent_container, text, command):
    responding_button = ttk.Button(parent_container, text=text, pad=(40, 20), style="Responding.Settings.TButton")
    responding_button['command'] = lambda: execute_command_and_flash_button(command, responding_button)
    return responding_button


def execute_command_and_flash_button(command, button):
    command()
    flash_button(button)


def flash_button(button, remaining_count=5):
    if button.instate(["alternate"]):
        button.state(["!alternate"])
    else:
        button.state(["alternate"])
    if remaining_count > 0:
        button.after(100, lambda: flash_button(button, remaining_count - 1))

def create_radio_button_with_text(master, text, compound=LEFT, **kwargs):
    if compound == LEFT:
        text_format = ' {}'
    elif compound == RIGHT:
        text_format = '{} '
    else:
        text_format = '{}'
    return ttk.Radiobutton(master, text=text_format.format(text), compound=compound, **kwargs)

def create_check_button_with_text(master, text, compound=LEFT, **kwargs):
    if compound == LEFT:
        text_format = ' {}'
    elif compound == RIGHT:
        text_format = '{} '
    else:
        text_format = '{}'
    return ttk.Checkbutton(master, text=text_format.format(text), compound=compound, **kwargs)
