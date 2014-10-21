from threading import Thread
import time


class Watchdog(Thread):
    def __init__(self, connection_list):
        Thread.__init__(self)
        self._connection_list = connection_list

    def run(self):
        while True:
            for client in self._connection_list:
                #print client
                time.sleep(1)

