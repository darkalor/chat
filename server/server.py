#!/usr/bin/python
import socket
import select
#import rsa
from collections import deque
import logging

logger = logging.getLogger('server')


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance


class Server(object):
    # Singleton
    __metaclass__ = Singleton

    _instance = None
    _connection_list = []
    _user_dict = {}
    _user_keys = {}
    _chat_history = deque(maxlen=10)

    def __init__(self, port, buffer=4096):
        self._port = port
        self._buffer = buffer
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(("0.0.0.0", self._port))
        self._socket.listen(10)
        self._connection_list.append(self._socket)
        #self.public_key, self.private_key = rsa.newkeys(512)

    def get_connection_list(self):
        return self._connection_list

    def broadcast(self, sock, message, sender=None):
        logger.info("Broadcasting message")
        # Append username if it is a message from other user
        if sender:
            message = sender + ": " + message
            self._chat_history.append(message)
        # Do not send the message to master socket and the client who has send us the message
        for connection in self._connection_list:
            if connection != self._socket and connection != sock:
                try:
                    logger.info("Sending message to: %s" % connection)
                    connection.send(message)
                except socket.error:
                    # broken socket connection may be, chat client pressed ctrl+c for example
                    logger.info("Closing socket connection")
                    connection.close()
                    self._connection_list.remove(connection)

    def broadcast_new_user(self, sock, username):
        logger.debug("Broadcasting about new user: %s" % username)
        self.broadcast(sock, "<users-add>" + username)

    def send_offline_user(self, sock, username):
        logger.debug("Broadcasting about removing user: %s" % username)
        self.broadcast(sock, "<users-remove>" + username)

    def make_offline(self, sock):
        logger.info("User went offline: %s" % sock)
        self.send_offline_user(sock, self._user_dict[sock])
        del self._user_dict[sock]
        sock.close()
        self._connection_list.remove(sock)

    def send_user_list_and_history(self, sock):
        logger.debug("Broadcasting user list and chat history to new user: %s" % sock)
        users = self._user_dict.values()
        history = "<history>" + "\n".join(self._chat_history)
        sock.send("<users>" + ",".join(users) + history)

    def handle_new_connection(self):
        # Handle the case in which there is a new connection received through server_socket
        connection, address = self._socket.accept()
        self._connection_list.append(connection)
        logger.info("Client (%s, %s) connected" % address)
        #self.send_key(connection)

    def send_private_message(self, data, sock):
        list = data.split(" ", 1)
        receiver = list[0][1:]
        message = list[1]
        logger.debug("Sending private message from: %s to %s" % (self._user_dict[sock], receiver))
        for conn, username in self._user_dict.items():
            if username == receiver:
                conn.send("From " + self._user_dict[sock] + ": " + message)

    def send_key(self, sock):
        sock.send('<key>' + str(self.public_key.n) + '<key>' + str(self.public_key.e))

    def handle_message(self, sock):
        try:
            data = sock.recv(self._buffer)
            if data:
                if sock in self._user_dict:
                    # Private message - "@username message"
                    if data.startswith("@"):
                        self.send_private_message(data, sock)
                    # Broadcast message - "message"
                    else:
                        self.broadcast(sock, data, self._user_dict[sock])
                # New user - "username"
                else:
                    #list = data.split('<end>')
                    self._user_dict[sock] = data
                    #self._user_keys[sock] = rsa.PublicKey(list[1], list[2])
                    self.broadcast_new_user(sock, data)
                    self.send_user_list_and_history(sock)
            # User disconnected
            else:
                self.make_offline(sock)
        # User disconnected
        except socket.error:
            self.make_offline(sock)

    def process_socket(self, read_sockets):
        for sock in read_sockets:
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
                read_sockets, write_sockets, error_sockets = select.select(self._connection_list, [], [])
                self.process_socket(read_sockets)
            except KeyboardInterrupt:
                logger.info("Exiting")
                self._socket.shutdown(socket.SHUT_RDWR)
                self._socket.close()
                exit()


if __name__ == "__main__":
    file_handler = logging.FileHandler('server.log')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    port = 5000
    server = Server(port)
    # TODO: implement
    # watchdog = Watchdog(server.get_connection_list())
    # watchdog.setDaemon(True)
    # watchdog.start()
    logger.info("Chat server started on port " + str(port))
    server.run()
