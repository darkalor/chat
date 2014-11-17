#!/usr/bin/python
from abc import ABCMeta, abstractmethod


class IClient(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def send(self, message):
        pass

    @abstractmethod
    def setDaemon(self, status):
        pass

    @abstractmethod
    def start(self):
        pass