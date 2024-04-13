import os
from tkinter import IntVar, StringVar, BooleanVar

SUDO = "sudo "
VNC_CONFIG_PATH = "/root/.vnc/config.d/vncserver-x11"
PORT_KEY = "RfbPort"
PASSWORD_KEY = "Password"
AUTHENTICATION_KEY = "Authentication"
DEFAULT_PORT = 5900
VNC_AUTHENTICATION = "VncAuth"
MIN_VNC_PASSWORD_LENGTH = 6

class VncConfig:
    instance = None


    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            #load config
            cls.instance = VncConfig()
        return cls.instance

    def __init__(self):
        self.port = IntVar(value=self.read_port_from_config_or_default())
        self.changePassword = BooleanVar()
        self.newPassword = StringVar()

    def read_port_from_config_or_default(self):
        port_value = self.read_value_from_config(PORT_KEY)
        if port_value is None:
            port_value = DEFAULT_PORT
        return port_value

    def read_value_from_config(self, key):
        command = SUDO + "grep -m 1 '^" + key + "=' " + VNC_CONFIG_PATH
        value_line = os.popen(command).read()
        return self.get_value_from_line(value_line, key)

    def get_value_from_line(self, value_line, key):
        if value_line.startswith(key + '='):
            return value_line.split(key + '=', 1)[1].strip()
        else:
            return None

    def save_and_apply(self):
        self.save_value(PORT_KEY, self.port.get())
        if self.changePassword.get():
            new_password = self.newPassword.get()
            if len(new_password) >= MIN_VNC_PASSWORD_LENGTH:
                command = "echo '" + new_password + "' | vncpasswd -print"
                obfuscated_password = self.get_value_from_line(os.popen(command).read(), PASSWORD_KEY)
                self.save_value(PASSWORD_KEY, obfuscated_password)
                self.save_value(AUTHENTICATION_KEY, VNC_AUTHENTICATION)
        os.system('sync')
        os.system(SUDO + "vncserver-x11 -service -reload")

    def save_value(self, key, value):
        commands = "grep -v  '^" + key + "=' " + VNC_CONFIG_PATH + " > tmp_file"\
                   + " && echo '" + key + "=" + str(value) + "' >> tmp_file "\
                   + " && mv tmp_file " + VNC_CONFIG_PATH
        os.system(SUDO + "bash -c \"" + commands + "\"")


