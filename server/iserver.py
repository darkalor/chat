#!/usr/bin/python
from abc import ABCMeta, abstractmethod

class IServer(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_connection_list(self):
        pass

    @abstractmethod
    def broadcast(self, sock, message, sender=None):
        pass

    @abstractmethod
    def send_new_user(self, sock, username):
        pass

    @abstractmethod
    def send_offline_user(self, sock, username):
        pass

    @abstractmethod
    def make_offline(self, sock):
        pass

    @abstractmethod
    def send_user_list_and_history(self, sock):
        pass

    @abstractmethod
    def handle_new_connection(self):
        pass

    @abstractmethod
    def send_private_message(self, data, sock):
        pass

    @abstractmethod
    def handle_message(self, sock):
        pass

    @abstractmethod
    def process_socket(self, read_sockets):
        pass

    @abstractmethod
    def run(self):
        pass
