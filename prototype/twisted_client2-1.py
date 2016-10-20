"""
This version contiains a user protocol for connecting to another application via localhost
But it does not do anything with inputs sent over from the client application

"""

from twisted.internet.protocol import Protocol, Factory
from twisted.protocols.basic import IntNStringReceiver, LineOnlyReceiver
from twisted.internet import task, defer, endpoints
import sys, socket, struct

from twisted.internet import reactor

hostName = 'YuchiLi-PC'
host = None
defaultTwistedServerPort = 8123
defaultUserPort = 5000

options = ['a', 'm', 'o', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

# use win32 reactor if applicable
if sys.platform == 'win32':
    from twisted.internet import win32eventreactor
    win32eventreactor.install()

# find hostname
def findHost():
    # TODO: error case for host not found
    addr = socket.gethostbyname(hostName)
    return addr

######################################################3

class UserProtocol(LineOnlyReceiver):
    def __init__(self):
        self.delimiter = '\n'
        self.socket_factory = None
        #TODO: specify max length of sent line

    def connectionMade(self):
        print ("connected to user program\ncreating socket factory\n\n")
        factory = SocketClientFactory()
        factory.originator = self

        self.socket_factory = factory   # store reference to socketClientProtocol
        self.factory.contactMade(self)  # store own reference in factory

        # instantiate TCP connection to twisted server
        reactor.connectTCP(host, defaultTwistedServerPort, factory)

    def lineReceived(self, line):
        print ("line received")

def UserFactory(Factory):

    protocol = UserProtocol

    def __init__(self):
        self.deferred = None    #TODO: callbacks needed?
        self.numConnections = 0
        self.connection = None
        #TODO: error check for when numConnections > 1

    # store single protocol reference
    def contactMade(self, connection):
        if self.numConnections >= 1:
            #TODO
            print ("error .. only one connection allowed")

        self.numConnections += 1
        self.connection = connection


class SocketClientProtocol(LineOnlyReceiver):

    # after int prefix and other framing are removed:
    def lineReceived(self, line):
        self.factory.got_msg(line)

    def connectionMade(self):   # calls when connection is made with Twisted server
        print ("connected to twisted server")
        self.factory.clientReady(self)


class SocketClientFactory(Factory):
    """ Created with callbacks for connection and receiving.
        send_msg can be used to send messages when connected.
    """
    protocol = SocketClientProtocol

    def __init__(
            self,
            connect_success_callback,
            connect_fail_callback,
            recv_callback):

        self.connect_success_callback = connect_success_callback
        self.connect_fail_callback = connect_fail_callback
        self.recv_callback = recv_callback

        # store reference to client
        self.client = None

    def clientConnectionFailed(self, connector, reason):
        # self.connect_fail_callback(reason)
        print ("connection failed")
        reactor.stop()

    def clientReady(self, client):
        self.client = client
        # self.connect_success_callback()

    def got_msg(self, msg):
        # self.recv_callback()
        self.originator.sendLine(msg)

    def send_msg(self, msg):
        if self.client:
            self.client.sendLine(msg)

###########################################

if __name__ == 'main':

    host = findHost()
    if(host is not None):

        user_server = UserFactory()
        reactor.listenTCP(defaultUserPort, user_server)

        reactor.run()