#!/usr/bin/python
import socket
import select
import sys
#import rsa
from threading import Thread
from common import MessageType as mt
from iclient import IClient


class Client(Thread, IClient):
    def __init__(self, app, host, port=5000):
        Thread.__init__(self)
        self._host = host
        self._port = port
        self.app = app
        self.user_list = []
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.public_key, self.private_key = rsa.newkeys(512)

    def send(self, message):
        self._socket.send(message)

    def connect(self):
        self._socket.connect((self._host, self._port))
        self._socket.settimeout(2)

    # data - <users>user1,user2<history>history
    def process_users_list(self, data):
        list = data.split("<history>")
        users = list[0]
        history = list[1]
        users = users[7:]
        if users:
            self.user_list = users.split(",")
            self.app.show_users(self.user_list)
        if history:
            self.app.display(history, message_type=mt.HISTORY)
        self.app.display('Welcome to the chat!', message_type=mt.INFO)

    # data - <users-add>new_user
    def process_add_user(self, data):
        data = data[11:]
        self.user_list.append(data)
        self.app.display("%s entered room" % data, message_type=mt.INFO)
        self.app.show_users(self.user_list)

    # data - <users-remove>removed_user
    def process_remove_user(self, data):
        data = data[14:]
        self.user_list.remove(data)
        self.app.display("%s left room" % data, message_type=mt.INFO)
        self.app.show_users(self.user_list)

    def process_data(self, data):
        if data.startswith("<users>"):
            self.process_users_list(data)
        elif data.startswith("<users-add>"):
            self.process_add_user(data)
        elif data.startswith("<users-remove>"):
            self.process_remove_user(data)
        else:
            # print data
            self.app.display(data)

    def run(self):
        try:
            self.connect()
            # TODO: move username later
            #self.send(self.app.get_username() + '<end>' + str(self.public_key.n) + '<end>' + str(self.public_key.e))
            self.send(self.app.get_username())
        except Exception as e:
            print e
            self.app.display('Unable to connect', message_type=mt.ERROR)
            sys.exit()

        socket_list = [self._socket]
        while 1:
            # Get the list sockets which are readable
            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

            for sock in read_sockets:
                #incoming message from remote server
                data = sock.recv(4096)
                if not data:
                    self.app.display('Disconnected from chat server', message_type=mt.ERROR)
                    sys.exit()
                else:
                    self.process_data(data)