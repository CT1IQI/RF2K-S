import time
from tkinter import BooleanVar, IntVar, StringVar, Tk

import interface
from config import Config
from display import Display

from sleepScreen import SleepScreen

CHECK_INTERVAL = 10000

MIN_MINUTES = 3
MAX_MINUTES = 60

ENABLED = 'On'
DISABLED = 'Off'


class SleepTimer:
    instance = None

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            # init instance
            cls.instance = SleepTimer()
        return cls.instance

    def __init__(self):
        self.mainApp = None
        self.display = Display.get_instance()
        self.lastActionTimeSeconds = time.monotonic()
        self.enabled = BooleanVar(value=Config.get_instance().sleepTimerConfig['enabled'])
        self.minutes = IntVar(value=Config.get_instance().sleepTimerConfig['minutes'])
        self.stateString = StringVar()
        self.sleepTimerJob = None
        self.activeSleepScreen = None
        self.apply_state()

    def observe(self, widget):
        if self.mainApp is None and isinstance(widget, Tk):
            self.mainApp = widget
            self.apply_state()
        widget.bind('<ButtonPress-1>', lambda _: self.reset())
        widget.bind('<Key>', lambda _: self.reset())

    def stop_observing(self, widget):
        if widget == self.mainApp and self.sleepTimerJob is not None:
            self.mainApp.after_cancel(self.sleepTimerJob)
            self.mainApp = None

    def apply_state(self):
        if self.enabled.get():
            self.enable()
            self.stateString.set(ENABLED)
        else:
            self.disable()
            self.stateString.set(DISABLED)

    def enable(self):
        if self.mainApp is not None:
            self.sleepTimerJob = self.mainApp.after(CHECK_INTERVAL, self.check_sleep_timer)

    def disable(self):
        if self.mainApp is not None and self.sleepTimerJob is not None:
            self.mainApp.after_cancel(self.sleepTimerJob)
            self.sleepTimerJob = None

    def check_sleep_timer(self):
        if time.monotonic() - self.lastActionTimeSeconds >= self.minutes.get() * 60:
            self.go_sleep()
        else:
            self.sleepTimerJob = self.mainApp.after(CHECK_INTERVAL, self.check_sleep_timer)

    def go_sleep(self):
        self.disable()
        self.activeSleepScreen = SleepScreen(self.mainApp, self.wake_up)
        self.activeSleepScreen.focus()
        self.display.off()
        interface.go_sleep()

    def wake_up(self):
        self.activeSleepScreen = None
        interface.wake_up()
        if Config.get_instance().displayOn.get():
            self.display.on()
        self.reset()
        self.enable()

    def reset(self):
        self.lastActionTimeSeconds = time.monotonic()

    def change_state(self):
        self.reset()
        self.enabled.set(not self.enabled.get())
        self.apply_state()
        self.save()

    def increment_minutes(self):
        self.reset()
        current = self.minutes.get()
        if current < MAX_MINUTES:
            self.minutes.set(current + 1)
        self.save()

    def decrement_minutes(self):
        self.reset()
        current = self.minutes.get()
        if current > MIN_MINUTES:
            self.minutes.set(current - 1)
        self.save()

    def save(self):
        Config.get_instance().sleepTimerConfig['enabled'] = self.enabled.get()
        Config.get_instance().sleepTimerConfig['minutes'] = self.minutes.get()
        Config.get_instance().save_sleep_timer_config()


