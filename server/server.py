#!/usr/bin/python
import socket
import select
from watchdog import Watchdog


class Server():

    _connectionList = []
    _userDict = {}

    def __init__(self, port, buffer=4096):
        self._port = port
        self._buffer = buffer
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(("0.0.0.0", self._port))
        self._socket.listen(10)
        self._connectionList.append(self._socket)

    def __del__(self):
        self._socket.close()

    def get_connection_list(self):
        return self._connectionList

    def broadcast(self, sock, message, sender=None):
        print "Message %s from %s" % (message, sock)
        #Do not send the message to master socket and the client who has send us the message
        for connection in self._connectionList:
            if connection != self._socket and connection != sock:
                try:
                    if sender:
                        connection.send(sender + ": " + message)
                    else:
                        connection.send(message)
                except socket.error as e:
                    # broken socket connection may be, chat client pressed ctrl+c for example
                    connection.close()
                    self._connectionList.remove(connection)

    def send_user_list(self, sock):
        users = self._userDict.values()
        sock.send("<users>" + ",".join(users))

    def send_new_user(self, sock, username):
        self.broadcast(sock, "<users-add>" + username)

    def send_offline_user(self, sock, username):
        self.broadcast(sock, "<users-remove>" + username)

    def make_offline(self, sock):
        self.send_offline_user(sock, self._userDict[sock])
        print "Client (%s, %s) is offline" % sock.getpeername()
        del self._userDict[sock]
        sock.close()
        self._connectionList.remove(sock)

    def handle_new_connection(self):
        # Handle the case in which there is a new connection received through server_socket
        connection, address = self._socket.accept()
        self._connectionList.append(connection)
        print "Client (%s, %s) connected" % address
        self.send_user_list(connection)

    def send_private_message(self, data, sock):
        list = data.split(" ", 1)
        receiver = list[0][1:]
        message = list[1]
        for conn, username in self._userDict.items():
            if username == receiver:
                conn.send("From " + self._userDict[sock] + ": " + message)

    def handle_message(self, sock):
        try:
            data = sock.recv(self._buffer)
            if data:
                if sock in self._userDict:
                    if data.startswith("@"):
                        self.send_private_message(data, sock)
                    else:
                        self.broadcast(sock, data, self._userDict[sock])
                else:
                    self._userDict[sock] = data
                    self.send_new_user(sock, data)
            else:
                self.make_offline(sock)
        except socket.error:
            self.make_offline(sock)

    def process_socket(self, readSockets):
        for sock in readSockets:
            # New connection
            if sock == self._socket:
                self.handle_new_connection()
            #Some incoming message from a client
            else:
                # Data received from client, process it
                self.handle_message(sock)

    def run(self):
        while 1:
            # Get the list sockets which are ready to be read through select
            try:
                readSockets, writeSockets, errorSockets = select.select(self._connectionList, [], [])

                self.process_socket(readSockets)
            except KeyboardInterrupt:
                print "Exiting"
                self._socket.shutdown(socket.SHUT_RDWR)
                self._socket.close()
                exit()


if __name__ == "__main__":
    port = 5000
    server = Server(port)
    watchdog = Watchdog(server.get_connection_list())
    watchdog.setDaemon(True)
    #TODO: implement
    #watchdog.start()
    print "Chat server started on port " + str(port)
    server.run()

