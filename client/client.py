#!/usr/bin/python
import socket
import select
import sys
from threading import Thread


class Client(Thread):
    def __init__(self, app, host, port=5000):
        Thread.__init__(self)
        self._host = host
        self._port = port
        self.app = app
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, message):
        self._socket.send(message)

    def connect(self):
        self._socket.connect((self._host, self._port))
        self._socket.settimeout(2)

    def run(self):
        try:
            self.connect()
        except:
            self.app.display('Unable to connect')
            sys.exit()

        self.app.display('Connected to remote host. Start sending messages')
        socket_list = [self._socket]
        while 1:
            # Get the list sockets which are readable
            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

            for sock in read_sockets:
                #incoming message from remote server
                data = sock.recv(4096)
                if not data:
                    self.app.display('Disconnected from chat server')
                    sys.exit()
                else:
                    #print data
                    self.app.display(data)