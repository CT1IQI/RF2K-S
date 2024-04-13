from datetime import datetime


def log(msg):
    print(str(datetime.now()) + " --- " + msg, flush=True)
