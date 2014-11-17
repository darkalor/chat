#!/usr/bin/python
import logging
from iapp import IApp
from common import MessageType as mt

logger = logging.getLogger('app')


class LogApp(IApp):

    def __init__(self, obj):
        self.obj = obj
        file_handler = logging.FileHandler('client.log')
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    def display(self, message, message_type=mt.TEXT):
        logger.debug("Received message: %s" % message)
        self.obj.display(message, message_type)

    def show_users(self, user_list):
        logger.debug("Updated user list: %s" % user_list)
        self.obj.show_users(user_list)

    def get_username(self):
        return self.obj.get_username()