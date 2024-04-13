from tkinter import ttk, Toplevel, FALSE, IntVar

import themes
from dimensions import DIMENSIONS

from cursorSetting import CursorSetting


class TurnOffDisplayAskScreen(Toplevel):

    def __init__(self, app, turn_off_callback, keep_on_callback):
        self.remaining_seconds_var = IntVar()
        self.turnOffCallback = turn_off_callback
        self.keepOnCallback = keep_on_callback
        self.app = app
        super().__init__(app)
        self.wait_visibility(self)
        self.attributes('-alpha', 0.9)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # get cursor managed
        CursorSetting.get_instance().manage_cursor_for(self)

        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.resizable(FALSE, FALSE)
        self.geometry(f"{DIMENSIONS.APP_WIDTH}x{DIMENSIONS.APP_HEIGHT}")

        frame = ttk.Frame(self)
        frame.grid(row=0, column=0, sticky="wnes")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(4, weight=1)

        question_frame = ttk.Frame(frame)
        question_frame.grid(row=1, column=0, pady=20)
        ttk.Label(question_frame, text="Display will turn off in ", style="Huge.TLabel").grid(row=0, column=0)
        ttk.Label(question_frame, textvariable=self.remaining_seconds_var, style="Huge.TLabel").grid(row=0, column=1)
        ttk.Label(question_frame, text=" seconds", style="Huge.TLabel").grid(row=0, column=2)

        answers_frame = ttk.Frame(frame)
        answers_frame.grid(row=2, column=0, pady=20)
        ttk.Button(answers_frame, text="Keep display on", command=self.keep_display_on, style="Button.Huge.TButton", pad=(20,10)).grid(row=0, column=0, sticky="nwes", padx=20)
        ttk.Button(answers_frame, text="Turn display off", command=self.turn_display_off, style="Button.Huge.TButton", pad=(20,10)).grid(row=0, column=1, sticky="nwes", padx=20)

        self.timerJob = None
        self.start_timer()

    def start_timer(self):
        self.remaining_seconds_var.set(10)
        self.timerJob = self.app.after(1000, self.step_timer)

    def step_timer(self):
        remaining = self.remaining_seconds_var.get()
        if remaining > 1:
            self.remaining_seconds_var.set(remaining - 1)
            self.timerJob = self.app.after(1000, self.step_timer)
        else:
            self.timerJob = None
            self.turn_display_off()

    def keep_display_on(self):
        self.keepOnCallback()
        self.close()

    def turn_display_off(self):
        self.turnOffCallback()
        self.close()

    def close(self):
        if self.timerJob is not None:
            self.app.after_cancel(self.timerJob)
        self.destroy()
        # window has to be removed from cursor management to prevent errors on next cursor change
        CursorSetting.get_instance().stop_managing_cursor_for(self)

