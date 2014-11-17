#!/usr/bin/python
from abc import ABCMeta, abstractmethod


class IApp(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def display(self, message):
        pass

    @abstractmethod
    def show_users(self, user_list):
        pass

    @abstractmethod
    def get_username(self):
        pass
