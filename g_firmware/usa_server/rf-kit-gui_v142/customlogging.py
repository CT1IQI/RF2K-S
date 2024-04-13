from datetime import datetime


def log(msg):
    print(str(datetime.now()) + " --- " + str(msg), flush=True)
