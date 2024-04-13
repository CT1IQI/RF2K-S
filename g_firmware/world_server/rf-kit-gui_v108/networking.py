import os
import re


def get_ip(interface_name):
    ip_info = re.search(re.compile(r'(?<=inet )(.*)(?=\/)', re.M), os.popen('ip addr show ' + interface_name).read())
    if ip_info is None:
        return "not connected"
    else:
        return ip_info.groups()[0]
