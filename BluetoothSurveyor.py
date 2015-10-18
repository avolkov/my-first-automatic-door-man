import atexit
import time
import os
import threading
from datetime import timedelta

class BluetoothSurveyor(object):

    def __init__(self):
        self.devices = {}

        # reset the devices output log file
        open('devices', 'w').close()

        # kill all previous instances of bluelog
        os.system("bluelog -k")

        # run bluelog as a deamon quiet and verbose, forgetting devices after 1 minute and logs to a file called "devices"
        os.system("bluelog -qvd -a 1 -o devices")

        # run the terminate method to finish bluelog's daemon
        atexit.register(terminate)

        time.sleep(1)
        self.file = open("devices","r")

        self.thread = threading.Thread(target=self.readLogFile)
        self.thread.daemon = True
        self.thread.start()

    def readLogFile(self):

        while True:
            line = self.file.readline()
            if not line:
                time.sleep(0.5)
                continue
            else:
                device = line.split()
                if len(device) == 1:
                    self.devices[device[0]] = time.time()

    def getDeviceLastSeenTimeByMAC(self, mac):

        if self.devices.has_key(mac):
            return self.devices[mac]
        else:
            return None

    def getDeviceLastSeenAgeInSecondsByMAC(self, mac):
        t = self.getDeviceLastSeenTimeByMAC(mac)

        if t is not None:
            delta = timedelta(0, time.time() - t)
            return delta.seconds
        else:
            return None

def terminate():
    print "Finishing bluelog..."
    os.system("bluelog -k")