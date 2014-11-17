#!/usr/bin/python
import logging
from iclient import IClient
from common import MessageType as mt

logger = logging.getLogger('client')


class LogClient(IClient):

    def __init__(self, obj):
        self.obj = obj
        file_handler = logging.FileHandler('client.log')
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    def send(self, message):
        logger.debug("Sent message: %s" % message)
        self.obj.send(message)

    def setDaemon(self, status):
        self.obj.setDaemon(status)

    def start(self):
        self.obj.start()