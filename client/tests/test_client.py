#!/usr/bin/python
import unittest
from client.client import Client
import socket
from mock import patch, MagicMock
from client.common import MessageType as mt


class TestClient(unittest.TestCase):

    def setUp(self):
        self.app = MagicMock()
        self.client = Client(self.app, 'localhost', 5000)

    def test_send(self):
        message = "test"
        with patch("socket.socket.send") as mock:
            self.client.send(message)
            self.assertEqual(mock.call_count, 1)
            self.assertEqual(mock.call_args[0][0], message)

    def test_connect(self):
        self.client._host = "localhost"
        self.client._port = 5000
        with patch("socket.socket.connect") as mock:
            self.client.connect()
            self.assertEqual(mock.call_count, 1)
            self.assertEqual(mock.call_args[0][0], (self.client._host, self.client._port))

    def test_process_users_list(self):
        user1 = "user1"
        user2 = "user2"
        history = "history"
        data = "<users>" + user1 + "," + user2 + "<history>" + history
        self.client.process_users_list(data)
        self.assertEqual(self.client.user_list, [user1, user2])
        self.assertEqual(self.app.show_users.call_count, 1)
        self.assertEqual(self.app.display.call_count, 2)
        self.assertEqual(self.app.display.call_args_list[0][0], (history,))

    def test_process_add_user(self):
        user = "user"
        data = "<users-add>" + user
        self.client.process_add_user(data)
        self.assertTrue(user in self.client.user_list)
        self.assertEqual(self.app.show_users.call_count, 1)
        self.assertEqual(self.app.show_users.call_args[0][0], self.client.user_list)
        self.assertEqual(self.app.display.call_count, 1)
        self.assertTrue(user in self.app.display.call_args[0][0])

    def test_process_remove_user(self):
        user = "user"
        self.client.user_list.append(user)
        data = "<users-remove>" + user
        self.client.process_remove_user(data)
        self.assertTrue(user not in self.client.user_list)
        self.assertEqual(self.app.show_users.call_count, 1)
        self.assertEqual(self.app.show_users.call_args[0][0], self.client.user_list)
        self.assertEqual(self.app.display.call_count, 1)
        self.assertTrue(user in self.app.display.call_args[0][0])

    def test_process_data_users_list(self):
        data = "<users>users<history>history"
        with patch("client.client.Client.process_users_list") as mock:
            self.client.process_data(data)
            self.assertEqual(mock.call_count, 1)
            self.assertEqual(mock.call_args[0][0], data)

    def test_process_data_new_user(self):
        data = "<users-add>user"
        with patch("client.client.Client.process_add_user") as mock:
            self.client.process_data(data)
            self.assertEqual(mock.call_count, 1)
            self.assertEqual(mock.call_args[0][0], data)

    def test_process_data_remove_user(self):
        data = "<users-remove>user"
        with patch("client.client.Client.process_remove_user") as mock:
            self.client.process_data(data)
            self.assertEqual(mock.call_count, 1)
            self.assertEqual(mock.call_args[0][0], data)

    def test_process_data_message(self):
        data = "message"
        self.client.process_data(data)
        self.assertEqual(self.app.display.call_count, 1)
        self.assertEqual(self.app.display.call_args[0][0], data)