import socket
import select
import sys


class Client():
    def __init__(self, host, port=5000):
        self._host = host
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def prompt(self):
        sys.stdout.write('<You> ')
        sys.stdout.flush()

    def connect(self):
        self._socket.connect((self._host, self._port))
        self._socket.settimeout(2)

    def run(self):
        try:
            self.connect()
        except:
            print 'Unable to connect'
            sys.exit()

        print 'Connected to remote host. Start sending messages'
        self.prompt()
        socket_list = [sys.stdin, self._socket]
        while 1:
            # Get the list sockets which are readable
            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

            for sock in read_sockets:
                #incoming message from remote server
                if sock == self._socket:
                    data = sock.recv(4096)
                    if not data:
                        print '\nDisconnected from chat server'
                        sys.exit()
                    else:
                        #print data
                        sys.stdout.write(data)
                        self.prompt()

                #user entered a message
                else:
                    msg = sys.stdin.readline()
                    self._socket.send(msg)
                    self.prompt()


#main function
if __name__ == "__main__":
    client = Client('localhost', 5000)
    client.run()

     
