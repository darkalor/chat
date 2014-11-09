#!/usr/bin/python
import socket
import select
import sys
from threading import Thread
from common import MessageType as mt

class Client(Thread):
    def __init__(self, app, host, port=5000):
        Thread.__init__(self)
        self._host = host
        self._port = port
        self.app = app
        self.user_list = []
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, message):
        self._socket.send(message)

    def connect(self):
        self._socket.connect((self._host, self._port))
        self._socket.settimeout(2)

    def run(self):
        try:
            self.connect()
            self.send(self.app.username)
        except:
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
                    if data.startswith("<users>"):
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
                    elif data.startswith("<users-add>"):
                        data = data[11:]
                        self.user_list.append(data)
                        self.app.display("%s entered room" % data, message_type=mt.INFO)
                        self.app.show_users(self.user_list)
                    elif data.startswith("<users-remove>"):
                        data = data[14:]
                        self.user_list.remove(data)
                        self.app.display("%s left room" % data, message_type=mt.INFO)
                        self.app.show_users(self.user_list)
                    else:
                        #print data
                        self.app.display(data)