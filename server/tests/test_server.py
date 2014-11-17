#!/usr/bin/python
import unittest
from server.server import Server
import socket
from mock import patch, MagicMock


class TestServer(unittest.TestCase):
    server = Server(5000)

    def setUp(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def tearDown(self):
        self.server._chat_history.clear()
        self.server._user_dict.clear()

    def test_singleton(self):
        s1 = Server(6000)
        s2 = Server(6000)
        self.assertEqual(id(s1), id(s2))

    def test_broadcast_with_sender(self):
        message = "Test message"
        sender = "Server"
        usr_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server._connection_list = []
        self.server._connection_list.append(usr_socket)
        with patch("socket.socket.send") as mock:
            self.server.broadcast(self.socket, message, sender)
            self.assertEqual(self.server._chat_history[0], sender + ": " + message)
            self.assertEqual(mock.call_count, 1)
            self.assertTrue(sender + ": " + message in mock.call_args[0])

    def test_broadcast_without_sender(self):
        message = "Test message"
        usr_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server._connection_list = []
        self.server._connection_list.append(usr_socket)
        with patch("socket.socket.send") as mock:
            self.assertEqual(len(self.server._chat_history), 0)
            self.server.broadcast(self.socket, message)
            self.assertEqual(mock.call_count, 1)
            self.assertTrue(message in mock.call_args[0])

    def test_broadcast_socket_exception(self):
        message = "Test message"
        usr_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server._connection_list = []
        self.server._connection_list.append(usr_socket)
        with patch("socket.socket.send", side_effect=socket.error) as mock:
            with patch("socket.socket.close") as mock2:
                self.server.broadcast(self.socket, message)
                self.assertEqual(mock.call_count, 1)
                self.assertTrue(message in mock.call_args[0])
                self.assertEqual(self.server._connection_list, [])
                self.assertEqual(mock2.call_count, 1)

    def test_broadcast_new_user(self):
        username = "test1"
        with patch("server.server.Server.broadcast") as mock:
            self.server.broadcast_new_user(self.socket, username)
            self.assertEqual(mock.call_count, 1)
            self.assertEqual(mock.call_args[0][1], "<users-add>" + username)

    def test_send_offline_user(self):
        username = "test1"
        with patch("server.server.Server.broadcast") as mock:
            self.server.send_offline_user(self.socket, username)
            self.assertEqual(mock.call_count, 1)
            self.assertEqual(mock.call_args[0][1], "<users-remove>" + username)

    def test_make_offline(self):
        username = "test1"
        usr_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server._connection_list = []
        self.server._connection_list.append(usr_socket)
        self.server._user_dict[usr_socket] = username
        with patch("socket.socket.close") as mock:
            with patch("server.server.Server.send_offline_user") as mock2:
                self.server.make_offline(usr_socket)
                self.assertEqual(mock2.call_args[0][1], username)
                self.assertEqual(mock.call_count, 1)
                self.assertTrue(usr_socket not in self.server._user_dict)
                self.assertEqual(self.server._connection_list, [])

    def test_send_user_list_and_history(self):
        username = "test1"
        message = "Test message"
        usr_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server._chat_history.append(message)
        self.server._user_dict[usr_socket] = username
        with patch("socket.socket.send") as mock:
            self.server.send_user_list_and_history(usr_socket)
            self.assertEqual(mock.call_args[0][0], "<users>" + username + "<history>" + message)

    def test_handle_new_connection(self):
        connection = self.socket
        address = ("127.0.0.1", "5000")
        with patch("socket.socket.accept", return_value=(connection, address)) as mock:
            self.server.handle_new_connection()
            self.assertEqual(mock.call_count, 1)
            self.assertTrue(connection in self.server._connection_list)

    def test_send_private_message(self):
        usr_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        receiver = "test1"
        sender = "test2"
        self.server._user_dict[usr_socket] = sender
        self.server._user_dict[self.socket] = receiver
        private_message = "Test message"
        data = "@" + receiver + " " + private_message
        with patch("socket.socket.send") as mock:
            self.server.send_private_message(data, usr_socket)
            self.assertEqual(mock.call_count, 1)
            self.assertEqual(mock.call_args[0][0], "From " + sender + ": " + private_message)

    def test_handle_message_private(self):
        message = "@test test"
        user = "test"
        sock = MagicMock(name='socket', spec=socket.socket)
        sock.recv.return_value = message
        self.server._user_dict[sock] = user
        with patch("server.server.Server.send_private_message") as mock_send:
            self.server.handle_message(sock)
            self.assertEqual(mock_send.call_count, 1)
            self.assertEqual(mock_send.call_args[0], (message, sock))

    def test_handle_message_broadcast(self):
        message = " test"
        user = "test"
        sock = MagicMock(name='socket', spec=socket.socket)
        sock.recv.return_value = message
        self.server._user_dict[sock] = user
        with patch("server.server.Server.broadcast") as mock_send:
            self.server.handle_message(sock)
            self.assertEqual(mock_send.call_count, 1)
            self.assertEqual(mock_send.call_args[0], (sock, message, user))

    def test_handle_message_new_user(self):
        username = "test"
        sock = MagicMock(name='socket', spec=socket.socket)
        sock.recv.return_value = username
        with patch("server.server.Server.broadcast_new_user") as mock_broadcast:
            with patch("server.server.Server.send_user_list_and_history") as mock_send:
                self.server.handle_message(sock)
                self.assertEqual(mock_broadcast.call_count, 1)
                self.assertEqual(mock_broadcast.call_args[0], (sock, username))
                self.assertEqual(mock_send.call_count, 1)
                self.assertEqual(mock_send.call_args[0][0], sock)
                self.assertEqual(self.server._user_dict[sock], username)

    def test_handle_message_disconnect(self):
        sock = MagicMock(name='socket', spec=socket.socket)
        sock.recv.return_value = None
        with patch("server.server.Server.make_offline") as mock:
            self.server.handle_message(sock)
            self.assertEqual(mock.call_count, 1)
            self.assertEqual(mock.call_args[0][0], sock)

    def test_process_socket_new_connection(self):
        read_sockets = []
        read_sockets.append(self.server._socket)
        with patch("server.server.Server.handle_new_connection") as mock:
            self.server.process_socket(read_sockets)
            self.assertEqual(mock.call_count, 1)

    def test_process_socket_existing_connection(self):
        read_sockets = []
        read_sockets.append(self.socket)
        with patch("server.server.Server.handle_message") as mock:
            self.server.process_socket(read_sockets)
            self.assertEqual(mock.call_count, 1)
            self.assertEqual(mock.call_args[0][0], self.socket)
