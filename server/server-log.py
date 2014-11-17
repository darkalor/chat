#!/usr/bin/python
import logging
from iserver import IServer
from server import Server

logger = logging.getLogger('server')

# TODO: add log messages here from Server
class ServerLog(IServer):

    def __init__(self, obj):
        self.obj = obj

    def get_connection_list(self):
        return self.obj.get_connection_list()

    def broadcast(self, sock, message, sender=None):
        logger.info("Broadcasting message")
        self.obj.broadcast(sock, message, sender=None)

    def send_new_user(self, sock, username):
        logger.debug("Broadcasting about new user: %s" % username)
        self.obj.send_new_user(sock, username)

    def send_offline_user(self, sock, username):
        logger.debug("Broadcasting about removing user: %s" % username)
        self.obj.send_offline_user(sock, username)

    def make_offline(self, sock):
        logger.info("User went offline: %s" % sock)
        self.obj.make_offline(sock)

    def send_user_list_and_history(self, sock):
        logger.debug("Broadcasting user list and chat history to new user: %s" % sock)
        self.obj.send_user_list_and_history(sock)

    def handle_new_connection(self):
        self.obj.handle_new_connection()

    def send_private_message(self, data, sock):
        self.obj.send_private_message(data, sock)

    def handle_message(self, sock):
        self.obj.handle_message(sock)

    def process_socket(self, read_sockets):
        self.obj.process_socket(read_sockets)

    def run(self):
        self.obj.run()


if __name__ == "__main__":
    file_handler = logging.FileHandler('server.log')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    port = 5000
    server = Server(port)
    watchdog = Watchdog(server.get_connection_list())
    watchdog.setDaemon(True)
    #TODO: implement
    #watchdog.start()
    logger.info("Chat server started on port " + str(port))
    server.run()
