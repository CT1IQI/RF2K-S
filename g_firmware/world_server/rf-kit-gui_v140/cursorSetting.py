from config import Config

CURSOR_ON = 'left_ptr'
CURSOR_OFF = 'none'


class CursorSetting:
    instance = None

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            # init instance
            cls.instance = CursorSetting()
        return cls.instance

    def __init__(self):
        self.managed_widgets = set()

    def manage_cursor_for(self, widget):
        self.managed_widgets.add(widget)
        self.update_cursor_for(widget)

    def stop_managing_cursor_for(self, widget):
        self.managed_widgets.remove(widget)

    def enable(self):
        if Config.get_instance().cursorVar.get() != CURSOR_ON:
            Config.get_instance().cursorVar.set(CURSOR_ON)
            self.update_widget_cursors_and_save()

    def disable(self):
        if Config.get_instance().cursorVar.get() != CURSOR_OFF:
            Config.get_instance().cursorVar.set(CURSOR_OFF)
            self.update_widget_cursors_and_save()

    def change_state(self):
        if Config.get_instance().cursorVar.get() != CURSOR_OFF:
            Config.get_instance().cursorVar.set(CURSOR_OFF)
        else:
            Config.get_instance().cursorVar.set(CURSOR_ON)
        self.update_widget_cursors_and_save()



    def update_widget_cursors_and_save(self):
        for widget in self.managed_widgets:
            self.update_cursor_for(widget)
        Config.get_instance().save_cursor()

    def update_cursor_for(self, widget):
        widget.configure(cursor=Config.get_instance().cursorVar.get())

