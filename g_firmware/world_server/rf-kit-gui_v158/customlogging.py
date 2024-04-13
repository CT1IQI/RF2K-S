import threading
import traceback
from datetime import datetime


def log(msg):
    thread = threading.current_thread()
    print(str(datetime.now()) + " --- [" + str(thread.getName()) + "(" + str(thread.ident) + ")] --- " + str(msg), flush=True)

def log_exc(msg, exctype, excvalue, tb):
    formatted_exception_lines = traceback.format_exception(exctype, excvalue, tb)
    thread = threading.current_thread()
    print(str(datetime.now()) + " --- [" + str(thread.getName()) + "(" + str(thread.ident) + ")] --- " + str(msg))
    print(*formatted_exception_lines, sep='\n', flush=True)

